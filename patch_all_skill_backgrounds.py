import pathlib

gradle_path = pathlib.Path("app/build.gradle")
main_activity_path = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")
billing_manager_path = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/BillingManager.kt")

gradle_text = gradle_path.read_text()
main_activity_text = main_activity_path.read_text()

errors = []


def apply_edit(text, old, new, marker, label, errors):
    if text.count(marker) >= 1:
        return text, False  # already applied
    count_old = text.count(old)
    if count_old == 1:
        return text.replace(old, new), True
    errors.append(f"{label}: expected exactly 1 match of old block (and marker absent), found old={count_old}")
    return text, False


# ============================================================
# 1. app/build.gradle - Play Billing Library dependency
# ============================================================
gradle_old = "    implementation 'io.ktor:ktor-client-android:3.1.1'\n}"
gradle_new = (
    "    implementation 'io.ktor:ktor-client-android:3.1.1'\n\n"
    "    // Google Play Billing - premium currency (Gems) purchases.\n"
    "    implementation 'com.android.billingclient:billing-ktx:9.1.0'\n"
    "}"
)
gradle_text, c1 = apply_edit(gradle_text, gradle_old, gradle_new, "com.android.billingclient:billing-ktx", "app/build.gradle billing dependency", errors)

# ============================================================
# 2. MainActivity.kt - billingManager property + startConnection()
# ============================================================
ma_old_1 = """class MainActivity : ComponentActivity() {
    private val gameViewModel: GameViewModel by viewModels()
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {"""
ma_new_1 = """class MainActivity : ComponentActivity() {
    private val gameViewModel: GameViewModel by viewModels()
    private val billingManager by lazy {
        BillingManager(this) { bundleId -> gameViewModel.creditPremiumCurrency(bundleId) }
    }
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        billingManager.startConnection()
        setContent {"""
main_activity_text, c2 = apply_edit(main_activity_text, ma_old_1, ma_new_1, "private val billingManager by lazy", "MainActivity.kt billingManager property", errors)

# ============================================================
# 3. MainActivity.kt - AppRoot call site + onDestroy lifecycle hook
# ============================================================
ma_old_2 = """                AppRoot(gameViewModel)
            }
        }
    }
override fun onPause() {
        super.onPause()
        gameViewModel.saveGame()
    }
}"""
ma_new_2 = """                AppRoot(gameViewModel, onLaunchPurchase = { bundleId -> billingManager.launchPurchase(this@MainActivity, bundleId) })
            }
        }
    }
override fun onPause() {
        super.onPause()
        gameViewModel.saveGame()
    }

    override fun onDestroy() {
        billingManager.endConnection()
        super.onDestroy()
    }
}"""
main_activity_text, c3 = apply_edit(main_activity_text, ma_old_2, ma_new_2, "override fun onDestroy() {", "MainActivity.kt AppRoot call site + onDestroy", errors)

# ============================================================
# 4. MainActivity.kt - AppRoot function signature
# ============================================================
ma_old_3 = "fun AppRoot(gameViewModel: GameViewModel) {"
ma_new_3 = "fun AppRoot(gameViewModel: GameViewModel, onLaunchPurchase: (String) -> Unit) {"
main_activity_text, c4 = apply_edit(main_activity_text, ma_old_3, ma_new_3, "fun AppRoot(gameViewModel: GameViewModel, onLaunchPurchase", "MainActivity.kt AppRoot signature", errors)

if errors:
    raise SystemExit(
        "PATCH B FAILED: one or more expected blocks did not match. No changes made to any file.\n"
        + "\n".join(f"  - {e}" for e in errors)
    )

# ============================================================
# 5. New file: BillingManager.kt (only created if it doesn't already exist)
# ============================================================
billing_manager_content = '''package com.yourname.idlerpg

import android.app.Activity
import android.content.Context
import android.util.Base64
import android.util.Log
import com.android.billingclient.api.BillingClient
import com.android.billingclient.api.BillingClientStateListener
import com.android.billingclient.api.BillingFlowParams
import com.android.billingclient.api.BillingResult
import com.android.billingclient.api.ConsumeParams
import com.android.billingclient.api.PendingPurchasesParams
import com.android.billingclient.api.ProductDetails
import com.android.billingclient.api.Purchase
import com.android.billingclient.api.PurchasesUpdatedListener
import com.android.billingclient.api.QueryProductDetailsParams
import com.android.billingclient.api.QueryPurchasesParams
import java.security.KeyFactory
import java.security.PublicKey
import java.security.Signature
import java.security.spec.X509EncodedKeySpec

// =========================================================
// GOOGLE PLAY BILLING - Premium currency (Gems) purchases.
//
// TODO before shipping: paste the app's Base64-encoded RSA public key
// from Play Console > Monetization setup > Licensing into
// LICENSE_PUBLIC_KEY_BASE64 below. Until that is filled in, ALL purchases
// are rejected (fail-closed) rather than silently accepted unverified.
//
// Product IDs below must be created in Play Console (Monetization >
// Products > In-app products) with EXACTLY these IDs, matching
// CurrencyBundleCatalog in MonetizationSystem.kt one-to-one:
// bundle_small, bundle_medium, bundle_large
// =========================================================

private const val LICENSE_PUBLIC_KEY_BASE64 = ""

class BillingManager(
    context: Context,
    private val onVerifiedPurchase: (bundleId: String) -> Unit
) {
    private val appContext = context.applicationContext
    private var productDetailsByBundleId: Map<String, ProductDetails> = emptyMap()

    private val purchasesUpdatedListener = PurchasesUpdatedListener { billingResult, purchases ->
        if (billingResult.responseCode == BillingClient.BillingResponseCode.OK && purchases != null) {
            purchases.forEach { handlePurchase(it) }
        } else {
            Log.w("BillingManager", "Purchase flow ended with code " + billingResult.responseCode + ": " + billingResult.debugMessage)
        }
    }

    private val billingClient: BillingClient = BillingClient.newBuilder(appContext)
        .setListener(purchasesUpdatedListener)
        .enablePendingPurchases(PendingPurchasesParams.newBuilder().enableOneTimeProducts().build())
        .enableAutoServiceReconnection()
        .build()

    fun startConnection() {
        if (billingClient.isReady) return
        billingClient.startConnection(object : BillingClientStateListener {
            override fun onBillingSetupFinished(billingResult: BillingResult) {
                if (billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
                    queryProducts()
                    queryExistingPurchases()
                } else {
                    Log.w("BillingManager", "Billing setup failed: " + billingResult.debugMessage)
                }
            }

            override fun onBillingServiceDisconnected() {
                // enableAutoServiceReconnection() handles reconnection automatically.
            }
        })
    }

    fun endConnection() {
        billingClient.endConnection()
    }

    private fun queryProducts() {
        val products = CurrencyBundleCatalog.bundles.map { bundle ->
            QueryProductDetailsParams.Product.newBuilder()
                .setProductId(bundle.id)
                .setProductType(BillingClient.ProductType.INAPP)
                .build()
        }
        val params = QueryProductDetailsParams.newBuilder().setProductList(products).build()
        billingClient.queryProductDetailsAsync(params) { billingResult, queryProductDetailsResult ->
            if (billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
                productDetailsByBundleId = queryProductDetailsResult.productDetailsList.associateBy { it.productId }
                if (queryProductDetailsResult.unfetchedProductList.isNotEmpty()) {
                    Log.w("BillingManager", "Unfetched products: " + queryProductDetailsResult.unfetchedProductList.map { it.productId })
                }
            } else {
                Log.w("BillingManager", "queryProductDetailsAsync failed: " + billingResult.debugMessage)
            }
        }
    }

    private fun queryExistingPurchases() {
        val params = QueryPurchasesParams.newBuilder()
            .setProductType(BillingClient.ProductType.INAPP)
            .build()
        billingClient.queryPurchasesAsync(params) { billingResult, purchases ->
            if (billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
                purchases.forEach { handlePurchase(it) }
            }
        }
    }

    fun launchPurchase(activity: Activity, bundleId: String) {
        val productDetails = productDetailsByBundleId[bundleId]
        if (productDetails == null) {
            Log.w("BillingManager", "No cached ProductDetails for " + bundleId + " - not ready yet.")
            return
        }
        val productDetailsParams = BillingFlowParams.ProductDetailsParams.newBuilder()
            .setProductDetails(productDetails)
            .build()
        val flowParams = BillingFlowParams.newBuilder()
            .setProductDetailsParamsList(listOf(productDetailsParams))
            .build()
        billingClient.launchBillingFlow(activity, flowParams)
    }

    private fun handlePurchase(purchase: Purchase) {
        if (purchase.purchaseState != Purchase.PurchaseState.PURCHASED) return
        if (!isSignatureValid(purchase)) {
            Log.w("BillingManager", "Purchase signature verification failed - not crediting Gems.")
            return
        }
        val bundleId = purchase.products.firstOrNull() ?: return
        onVerifiedPurchase(bundleId)

        val consumeParams = ConsumeParams.newBuilder()
            .setPurchaseToken(purchase.purchaseToken)
            .build()
        billingClient.consumeAsync(consumeParams) { billingResult, _ ->
            if (billingResult.responseCode != BillingClient.BillingResponseCode.OK) {
                Log.w("BillingManager", "consumeAsync failed: " + billingResult.debugMessage)
            }
        }
    }

    private fun isSignatureValid(purchase: Purchase): Boolean {
        if (LICENSE_PUBLIC_KEY_BASE64.isBlank()) {
            Log.e("BillingManager", "LICENSE_PUBLIC_KEY_BASE64 is not set - rejecting all purchases until Play Console licensing key is configured.")
            return false
        }
        return try {
            val publicKey = generatePublicKey(LICENSE_PUBLIC_KEY_BASE64)
            val signatureAlgorithm = Signature.getInstance("SHA1withRSA")
            signatureAlgorithm.initVerify(publicKey)
            signatureAlgorithm.update(purchase.originalJson.toByteArray())
            signatureAlgorithm.verify(Base64.decode(purchase.signature, Base64.DEFAULT))
        } catch (e: Exception) {
            Log.e("BillingManager", "Signature verification error", e)
            false
        }
    }

    private fun generatePublicKey(base64Key: String): PublicKey {
        val keyBytes = Base64.decode(base64Key, Base64.DEFAULT)
        val keyFactory = KeyFactory.getInstance("RSA")
        return keyFactory.generatePublic(X509EncodedKeySpec(keyBytes))
    }
}
'''

billing_manager_created = False
if not billing_manager_path.exists():
    billing_manager_path.write_text(billing_manager_content)
    billing_manager_created = True

gradle_path.write_text(gradle_text)
main_activity_path.write_text(main_activity_text)

any_changed = any([c1, c2, c3, c4]) or billing_manager_created
if any_changed:
    print("Patch B applied:")
    print("  - app/build.gradle: added com.android.billingclient:billing-ktx:9.1.0")
    print("  - BillingManager.kt: " + ("created new file" if billing_manager_created else "already existed, left untouched"))
    print("  - MainActivity.kt: billingManager property + startConnection()/endConnection() lifecycle, AppRoot signature + call site updated")
    print("")
    print("NOTE: LICENSE_PUBLIC_KEY_BASE64 in BillingManager.kt is still blank - all purchases will be rejected (fail-closed) until you paste in the Play Console licensing key.")
else:
    print("Patch B: already fully applied, no changes made.")
