package com.yourname.idlerpg

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
