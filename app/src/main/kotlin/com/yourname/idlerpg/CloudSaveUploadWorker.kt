package com.yourname.idlerpg

import android.content.Context
import androidx.work.Constraints
import androidx.work.CoroutineWorker
import androidx.work.ExistingWorkPolicy
import androidx.work.NetworkType
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.WorkerParameters

class CloudSaveUploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val prefs = applicationContext.getSharedPreferences(
            PREFS_NAME,
            Context.MODE_PRIVATE
        )

        repeat(100) {
            val pending = synchronized(lock) {
                val pendingKey = prefs.all.keys
                    .filter { it.startsWith(KEY_CHARACTER_ID_PREFIX) }
                    .sorted()
                    .firstOrNull()

                if (pendingKey != null) {
                    val characterId = pendingKey.removePrefix(KEY_CHARACTER_ID_PREFIX)
                    val json = prefs.getString(KEY_SAVE_JSON_PREFIX + characterId, null)
                    if (json == null) null else characterId to json
                } else {
                    // Migrate the old single pending slot without discarding it.
                    val id = prefs.getString(KEY_CHARACTER_ID, null)
                    val json = prefs.getString(KEY_SAVE_JSON, null)

                    if (id == null || json == null) {
                        null
                    } else {
                        val migrated = prefs.edit()
                            .putString(KEY_CHARACTER_ID_PREFIX + id, id)
                            .putString(KEY_SAVE_JSON_PREFIX + id, json)
                            .remove(KEY_CHARACTER_ID)
                            .remove(KEY_SAVE_JSON)
                            .commit()

                        if (migrated) id to json else null
                    }
                }
            } ?: return Result.success()

            val characterId = pending.first
            val saveJson = pending.second

            // Never upload unless the save contains exactly the local character
            // mapped to this Supabase character.
            val mappedLocalId = SupabaseCharacterRepository
                .getCharacterLocalId(characterId)
                .getOrElse { return Result.retry() }

            if (mappedLocalId.isNullOrBlank()) {
                return Result.failure()
            }

            val containsMappedCharacter = runCatching {
                val root = org.json.JSONObject(saveJson)
                val accounts = root.optJSONArray("accounts")
                val characters = root.optJSONArray("characters")

                val hasSingleScopedIdentity =
                    accounts != null &&
                    accounts.length() == 1 &&
                    characters != null &&
                    characters.length() == 1 &&
                    characters.getJSONObject(0).optString("id") == mappedLocalId &&
                    characters.getJSONObject(0).optString("accountId").isNotBlank() &&
                    accounts.getJSONObject(0).optString("id") ==
                        characters.getJSONObject(0).optString("accountId")

                val skills = root.optJSONArray("skills")
                val skillIds = mutableSetOf<String>()
                var validSkills = skills != null && skills.length() == 16

                if (skills != null) {
                    for (index in 0 until skills.length()) {
                        val skill = skills.optJSONObject(index)
                        if (skill == null) {
                            validSkills = false
                            continue
                        }
                        val skillId = skill.optString("skillId")
                        val skillCharacterId = skill.optString("characterId")
                        val xp = skill.optLong("xp", -1L)
                        if (
                            skillCharacterId != mappedLocalId ||
                            skillId.isBlank() ||
                            xp < 0L ||
                            !skillIds.add(skillId)
                        ) {
                            validSkills = false
                        }
                    }
                }

                // Every character-owned array in a cloud payload must belong
                // to this one mapped character. This also rejects old queued
                // full-device snapshots and orphaned progression records.
                val characterScopedArrays = listOf(
                    "skillingQueues",
                    "craftingQueues",
                    "lastSeen",
                    "lastSaleCheck",
                    "inventoryItems",
                    "equippedSlots",
                    "loadoutSettings",
                    "marketAccounts",
                    "marketOrders",
                    "combatSessions",
                    "offlineCombatQueues",
                    "buryQueues"
                )
                val validScopedData = characterScopedArrays.all { name ->
                    val entries = root.optJSONArray(name)
                    entries == null || (0 until entries.length()).all { index ->
                        entries.optJSONObject(index)
                            ?.optString("characterId") == mappedLocalId
                    }
                }

                hasSingleScopedIdentity &&
                    validSkills &&
                    skillIds.size == 16 &&
                    validScopedData
            }.getOrDefault(false)

            if (!containsMappedCharacter) {
                // Keep invalid pending JSON intact for manual recovery.
                return Result.failure()
            }

            // Network operation must remain outside synchronized(lock).
            val upload = SupabaseCharacterRepository.uploadCharacterSave(
                characterId,
                saveJson
            )

            if (upload.isFailure) {
                return Result.retry()
            }

            val finished = synchronized(lock) {
                val latestJson = prefs.getString(
                    KEY_SAVE_JSON_PREFIX + characterId,
                    null
                )

                if (latestJson == saveJson) {
                    prefs.edit()
                        .remove(KEY_CHARACTER_ID_PREFIX + characterId)
                        .remove(KEY_SAVE_JSON_PREFIX + characterId)
                        .commit()
                } else {
                    false
                }
            }

            if (!finished) {
                return Result.retry()
            }
        }

        // More than 100 saves were queued; continue draining on the next run.
        return Result.retry()
    }

    companion object {
        private const val PREFS_NAME = "pending_cloud_save"

        // Each character has its own pending slot so switching characters
        // cannot overwrite another character's unsent save.
        private const val KEY_CHARACTER_ID_PREFIX = "character_id_"
        private const val KEY_SAVE_JSON_PREFIX = "save_json_"

        // Legacy single-slot keys are read during migration/recovery only.
        private const val KEY_CHARACTER_ID = "character_id"
        private const val KEY_SAVE_JSON = "save_json"
        private const val UNIQUE_WORK_NAME = "idlerpg_cloud_save_upload"

        private val lock = Any()

        fun pendingCombatQueueDiagnostic(context: Context): String {
            val prefs = context.applicationContext.getSharedPreferences(
                PREFS_NAME,
                Context.MODE_PRIVATE
            )

            val pendingSaves = synchronized(lock) {
                val entries = prefs.all.keys
                    .filter { it.startsWith(KEY_CHARACTER_ID_PREFIX) }
                    .sorted()
                    .mapNotNull { key ->
                        val id = key.removePrefix(KEY_CHARACTER_ID_PREFIX)
                        val json = prefs.getString(KEY_SAVE_JSON_PREFIX + id, null)
                        if (json == null) null else id to json
                    }
                    .toMutableList()

                val legacyId = prefs.getString(KEY_CHARACTER_ID, null)
                val legacyJson = prefs.getString(KEY_SAVE_JSON, null)

                if (legacyId != null && legacyJson != null) {
                    entries += legacyId to legacyJson
                }

                entries
            }

            if (pendingSaves.isEmpty()) return "Pending upload: none"

            return try {
                pendingSaves.joinToString("\n\n") { pending ->
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
                }
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
                prefs.getString(KEY_SAVE_JSON_PREFIX + characterId, null) != null ||
                    (
                        prefs.getString(KEY_CHARACTER_ID, null) == characterId &&
                            prefs.getString(KEY_SAVE_JSON, null) != null
                    )
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
                    .putString(KEY_CHARACTER_ID_PREFIX + characterId, characterId)
                    .putString(KEY_SAVE_JSON_PREFIX + characterId, saveJson)
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

            val hasLegacyPending =
                prefs.getString(KEY_CHARACTER_ID, null) != null &&
                    prefs.getString(KEY_SAVE_JSON, null) != null

            val hasScopedPending = prefs.all.keys.any {
                it.startsWith(KEY_CHARACTER_ID_PREFIX)
            }

            if (hasLegacyPending || hasScopedPending) {
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
