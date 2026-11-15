
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
            val pending = synchronized(lock) {
                val id = prefs.getString(KEY_CHARACTER_ID, null)
                val json = prefs.getString(KEY_SAVE_JSON, null)

                if (id == null || json == null) {
                    null
                } else {
                    id to json
                }
            } ?: return Result.success()

            
            val characterId = pending.first
            val saveJson = pending.second

            // Never upload a save unless it contains the local character
            // currently mapped to this Supabase character.
            val mappedLocalId = SupabaseCharacterRepository
                .getCharacterLocalId(characterId)
                .getOrElse { return Result.retry() }

            if (mappedLocalId.isNullOrBlank()) {
                return Result.failure()
            }

            val containsMappedCharacter = runCatching {
                val root = org.json.JSONObject(saveJson)

                val characters = root.optJSONArray("characters")
                val hasCharacterRecord = characters != null &&
                    (0 until characters.length()).any { index ->
                        characters.getJSONObject(index)
                            .optString("id") == mappedLocalId
                    }

                val skills = root.optJSONArray("skills")
                val hasCompleteSkillRecord = skills != null &&
                    (0 until skills.length()).count { index ->
                        skills.getJSONObject(index)
                            .optString("characterId") == mappedLocalId
                    } >= 16

                val inventory = root.optJSONArray("inventoryItems")
                val hasInventoryRecord = inventory != null &&
                    (0 until inventory.length()).any { index ->
                        inventory.getJSONObject(index)
                            .optString("characterId") == mappedLocalId
                    }

                hasCharacterRecord ||
                    (hasCompleteSkillRecord && hasInventoryRecord)
            }.getOrDefault(false)

            if (!containsMappedCharacter) {
                // Keep the pending JSON intact for recovery.
                return Result.failure()
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
                } else {
                    false
                }
            }

            if (finished) {
                return Result.success()
            }
        }

        return Result.retry()
    }

    companion object {
        private const val PREFS_NAME = "pending_cloud_save"
        private const val KEY_CHARACTER_ID = "character_id"
        private const val KEY_SAVE_JSON = "save_json"
        private const val UNIQUE_WORK_NAME = "idlerpg_cloud_save_upload"

        private val lock = Any()
        
        fun pendingCombatQueueDiagnostic(context: Context): String {
            val prefs = context.applicationContext.getSharedPreferences(
                PREFS_NAME,
                Context.MODE_PRIVATE
            )

            val pending = synchronized(lock) {
                val id = prefs.getString(KEY_CHARACTER_ID, null)
                val json = prefs.getString(KEY_SAVE_JSON, null)
                if (id == null || json == null) null else id to json
            } ?: return "Pending upload: none"

            return try {
                val root = org.json.JSONObject(pending.second)
                val sections = mutableListOf<String>()

                fun summarizeArray(
                    name: String,
                    description: (org.json.JSONObject) -> String
                ) {
                    val queues = root.optJSONArray(name)
                    if (queues != null && queues.length() > 0) {
                        val entries = (0 until queues.length()).joinToString("; ") { index ->
                            description(queues.getJSONObject(index))
                        }
                        sections += "$name: $entries"
                    } else {
                        sections += "$name: none"
                    }
                }

                summarizeArray("skillingQueues") { queue ->
                    "character=${queue.optString("characterId")}, " +
                        "skill=${queue.optString("skillId")}, " +
                        "item=${queue.optString("itemId")}"
                }

                summarizeArray("craftingQueues") { queue ->
                    "character=${queue.optString("characterId")}, " +
                        "recipe=${queue.optString("recipeId")}"
                }

                summarizeArray("offlineCombatQueues") { queue ->
                    "character=${queue.optString("characterId")}, " +
                        "zone=${queue.optString("zoneId")}"
                }

                summarizeArray("buryQueues") { queue ->
                    "character=${queue.optString("characterId")}, " +
                        "item=${queue.optString("itemId")}"
                }

                "Pending upload character=${pending.first}\n" +
                    sections.joinToString("\n")
            } catch (e: Exception) {
                "Pending upload exists, but its queue data could not be read: " +
                    (e.message ?: "unknown error")
            }
        }
            
        fun hasPendingUploadFor(
            context: Context,
            characterId: String
        ): Boolean {
            val prefs = context.applicationContext.getSharedPreferences(
                PREFS_NAME,
                Context.MODE_PRIVATE
            )

            return synchronized(lock) {
                prefs.getString(KEY_CHARACTER_ID, null) == characterId &&
                    prefs.getString(KEY_SAVE_JSON, null) != null
            }
        
        }
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
            val appContext = context.applicationContext
            val prefs = appContext.getSharedPreferences(
                PREFS_NAME,
                Context.MODE_PRIVATE
            )

            if (
                prefs.getString(KEY_CHARACTER_ID, null) != null &&
                prefs.getString(KEY_SAVE_JSON, null) != null
            ) {
                enqueue(appContext)
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
                ExistingWorkPolicy.APPEND_OR_REPLACE,
                request
            )

        }
    }
}
