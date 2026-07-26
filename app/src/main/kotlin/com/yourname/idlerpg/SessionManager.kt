package com.yourname.idlerpg.data

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class SessionManager(context: Context) {
    private val prefs: SharedPreferences

    init {
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()

        prefs = EncryptedSharedPreferences.create(
            context,
            "idlerpg_session",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }

    fun saveSession(accountId: String) {
        prefs.edit().putString(KEY_ACCOUNT_ID, accountId).apply()
    }

    fun getSavedAccountId(): String? = prefs.getString(KEY_ACCOUNT_ID, null)

    fun clearSession() {
        prefs.edit().remove(KEY_ACCOUNT_ID).apply()
    }

    companion object {
        private const val KEY_ACCOUNT_ID = "account_id"
    }
}
