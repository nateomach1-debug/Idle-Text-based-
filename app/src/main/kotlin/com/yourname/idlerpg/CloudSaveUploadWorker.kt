
package com.yourname.idlerpg

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import androidx.work.WorkManager
import androidx.work.Constraints
import androidx.work.NetworkType
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.ExistingWorkPolicy

class CloudSaveUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val prefs = applicationContext.getSharedPreferences(
            PREFS_NAME,
            Context.MODE_PRIVATE
        )

        repeat(5) {
            val characterId: String
            val saveJson: String

            synchronized(lock) {
                characterId = prefs.getString(KEY_CHARACTER_ID, null)
                    ?: return Result.success()

                saveJson = prefs.getString(KEY_SAVE_JSON, null)
                    ?: return Result.success()
            }

            val upload = SupabaseCharacterRepository.uploadCharacterSave(
                characterId,
                saveJson
            )

            if (upload.isFailure) {
                return Result.retry()
            }

            val finished = synchronized(lock) {
                val latestId = prefs.getString(KEY_CHARACTER_ID, null)
                val latestJson = prefs.getString(KEY_SAVE_JSON, null)

                if (latestId == characterId && latestJson == saveJson) {
                    prefs.edit()
                        .remove(KEY_CHARACTER_ID)
                        .remove(KEY_SAVE_JSON)
                        .commit()
                    true
                } else {
                    false
                }
            }

            if (finished) {
                return Result.success()
            }
        }

        // More saves arrived while uploading. Retry to process the newest one.
        return Result.retry()
    }

    companion object {
        private const val PREFS_NAME = "pending_cloud_save"
        private const val KEY_CHARACTER_ID = "character_id"
        private const val KEY_SAVE_JSON = "save_json"
        private const val UNIQUE_WORK_NAME = "idlerpg_cloud_save_upload"

        private val lock = Any()

        fun storeAndEnqueue(
            context: Context,
            characterId: String,
            saveJson: String
        ): Boolean {
            val appContext = context.applicationContext

            val saved = synchronized(lock) {
                appContext.getSharedPreferences(
                    PREFS_NAME,
                    Context.MODE_PRIVATE
                ).edit()
                    .putString(KEY_CHARACTER_ID, characterId)
                    .putString(KEY_SAVE_JSON, saveJson)
                    .commit()
            }

            if (!saved) return false

            enqueue(appContext)
            return true
        }

        fun enqueuePending(context: Context) {
            val prefs = context.applicationContext.getSharedPreferences(
                PREFS_NAME,
                Context.MODE_PRIVATE
            )

            if (
                prefs.getString(KEY_CHARACTER_ID, null) != null &&
                prefs.getString(KEY_SAVE_JSON, null) != null
            ) {
                enqueue(context.applicationContext)
            }
        }

        private fun enqueue(context: Context) {
            val constraints = Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build()

            val request =
                OneTimeWorkRequestBuilder<CloudSaveUploadWorker>()
                    .setConstraints(constraints)
                    .build()

            WorkManager.getInstance(context).enqueueUniqueWork(
                UNIQUE_WORK_NAME,
                ExistingWorkPolicy.REPLACE,
                request
       
            )
        }
    }
}
