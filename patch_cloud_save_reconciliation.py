"""
Cloud save reconciliation - the Kotlin half of the moderator-leak fix.

After the SQL fix (get_or_create_character no longer creates a second
character under an existing profile), the client needs to actually DO
something useful when the server hands back an existing character
instead of a fresh one: download that character's real save and apply
it, discarding the throwaway local character that was just created.

Also wires up background upload of the local save after every local
save, so there's something real to download later.

Touches: GameStateRepository.kt, SupabaseCharacterRepository.kt,
GameViewModel.kt. Guarded with asserts.
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"

# ---------------------------------------------------------------
# 1. GameStateRepository.kt - expose raw JSON read/write
# ---------------------------------------------------------------
path = os.path.join(BASE, "GameStateRepository.kt")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = '    private val saveFile: File get() = File(context.filesDir, "game_state.json")\n'
new = (
    '    private val saveFile: File get() = File(context.filesDir, "game_state.json")\n'
    "\n"
    "    // Exposes the exact JSON already written by save() - reused as-is as\n"
    "    // the cloud upload payload, so no separate serialization format is needed.\n"
    "    fun currentSaveJson(): String? = if (saveFile.exists()) saveFile.readText() else null\n"
    "\n"
    "    // Used when restoring a character's save downloaded from the cloud -\n"
    "    // overwrites local state with the recovered JSON before re-loading it.\n"
    "    fun overwriteRawJson(json: String) {\n"
    "        saveFile.writeText(json)\n"
    "    }\n"
)
assert old in content, "saveFile anchor not found in GameStateRepository.kt"
assert content.count(old) == 1, "saveFile anchor not unique"
content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Patched GameStateRepository.kt")

# ---------------------------------------------------------------
# 2. SupabaseCharacterRepository.kt - add 3 new functions
# ---------------------------------------------------------------
path = os.path.join(BASE, "SupabaseCharacterRepository.kt")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = (
    "import io.github.jan.supabase.postgrest.postgrest\n"
    "import kotlinx.serialization.json.buildJsonObject\n"
    "import kotlinx.serialization.json.put\n"
)
new = (
    "import io.github.jan.supabase.postgrest.postgrest\n"
    "import kotlinx.serialization.json.Json\n"
    "import kotlinx.serialization.json.JsonElement\n"
    "import kotlinx.serialization.json.buildJsonObject\n"
    "import kotlinx.serialization.json.put\n"
)
assert old in content, "imports anchor not found in SupabaseCharacterRepository.kt"
assert content.count(old) == 1, "imports anchor not unique"
content = content.replace(old, new)

old = (
    "    suspend fun getOrCreateCharacter(localCharacterId: String, displayName: String): Result<String> = runCatching {\n"
    "        client.postgrest.rpc(\"get_or_create_character\", buildJsonObject {\n"
    "            put(\"p_local_character_id\", localCharacterId)\n"
    "            put(\"p_display_name\", displayName)\n"
    "        }).decodeAs<String>()\n"
    "    }\n"
    "}\n"
)
new = (
    "    suspend fun getOrCreateCharacter(localCharacterId: String, displayName: String): Result<String> = runCatching {\n"
    "        client.postgrest.rpc(\"get_or_create_character\", buildJsonObject {\n"
    "            put(\"p_local_character_id\", localCharacterId)\n"
    "            put(\"p_display_name\", displayName)\n"
    "        }).decodeAs<String>()\n"
    "    }\n"
    "\n"
    "    // Lets the caller detect a local_character_id mismatch after\n"
    "    // getOrCreateCharacter - a mismatch means an EXISTING character (from a\n"
    "    // different device/install) was returned, not a fresh one.\n"
    "    suspend fun getCharacterLocalId(characterId: String): Result<String?> = runCatching {\n"
    "        client.postgrest.rpc(\"get_character_local_id\", buildJsonObject {\n"
    "            put(\"p_character_id\", characterId)\n"
    "        }).decodeAs<String?>()\n"
    "    }\n"
    "\n"
    "    // Uploads the local save JSON as-is (round-tripped through kotlinx's\n"
    "    // JSON parser since org.json and kotlinx.serialization are different\n"
    "    // libraries in this codebase) as this character's cloud backup.\n"
    "    suspend fun uploadCharacterSave(characterId: String, saveJson: String): Result<Unit> = runCatching {\n"
    "        val parsed: JsonElement = Json.parseToJsonElement(saveJson)\n"
    "        client.postgrest.rpc(\"upload_character_save\", buildJsonObject {\n"
    "            put(\"p_character_id\", characterId)\n"
    "            put(\"p_save_data\", parsed)\n"
    "        })\n"
    "        Unit\n"
    "    }\n"
    "\n"
    "    // Downloads this character's cloud backup, returned as the same raw\n"
    "    // JSON string shape GameStateRepository already reads/writes locally.\n"
    "    suspend fun downloadCharacterSave(characterId: String): Result<String?> = runCatching {\n"
    "        val result = client.postgrest.rpc(\"download_character_save\", buildJsonObject {\n"
    "            put(\"p_character_id\", characterId)\n"
    "        }).decodeAs<JsonElement?>()\n"
    "        result?.toString()\n"
    "    }\n"
    "}\n"
)
assert old in content, "getOrCreateCharacter anchor not found in SupabaseCharacterRepository.kt"
assert content.count(old) == 1, "getOrCreateCharacter anchor not unique"
content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Patched SupabaseCharacterRepository.kt")

# ---------------------------------------------------------------
# 3. GameViewModel.kt - background upload after save + reconciliation
# ---------------------------------------------------------------
path = os.path.join(BASE, "GameViewModel.kt")
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 3a. Background upload right after the save() call completes.
old = (
    "            inventoryService.exportAllItems(),\n"
    "            inventoryService.exportAllEquipped(),\n"
    "            inventoryService.exportAllLoadoutSettings(),\n"
    "            marketService.exportAccounts(),\n"
    "            marketService.exportOrders(),\n"
    "            marketService.exportPriceHistory()\n"
    "        )\n"
    "    }\n"
)
new = (
    "            inventoryService.exportAllItems(),\n"
    "            inventoryService.exportAllEquipped(),\n"
    "            inventoryService.exportAllLoadoutSettings(),\n"
    "            marketService.exportAccounts(),\n"
    "            marketService.exportOrders(),\n"
    "            marketService.exportPriceHistory()\n"
    "        )\n"
    "        val supabaseCharacterId = _currentSupabaseCharacterId.value\n"
    "        val json = repository.currentSaveJson()\n"
    "        if (supabaseCharacterId != null && json != null) {\n"
    "            viewModelScope.launch {\n"
    "                SupabaseCharacterRepository.uploadCharacterSave(supabaseCharacterId, json)\n"
    "            }\n"
    "        }\n"
    "    }\n"
)
assert old in content, "save-tail anchor not found in GameViewModel.kt"
assert content.count(old) == 1, "save-tail anchor not unique"
content = content.replace(old, new)

# 3b. Reconciliation in selectCharacter().
old = (
    "            viewModelScope.launch {\n"
    "                val result = SupabaseCharacterRepository.getOrCreateCharacter(characterId, selectedCharacter.displayName)\n"
    "                result.onFailure { _characterSyncError.value = it.message ?: it.toString() }\n"
    "                result.onSuccess { _characterSyncError.value = null }\n"
    "                _currentSupabaseCharacterId.value = result.getOrNull()\n"
    "            }\n"
)
new = (
    "            viewModelScope.launch {\n"
    "                val result = SupabaseCharacterRepository.getOrCreateCharacter(characterId, selectedCharacter.displayName)\n"
    "                result.onFailure { _characterSyncError.value = it.message ?: it.toString() }\n"
    "                result.onSuccess { _characterSyncError.value = null }\n"
    "                _currentSupabaseCharacterId.value = result.getOrNull()\n"
    "                val supabaseCharacterId = result.getOrNull()\n"
    "                if (supabaseCharacterId != null) {\n"
    "                    val remoteLocalId = SupabaseCharacterRepository.getCharacterLocalId(supabaseCharacterId).getOrNull()\n"
    "                    if (remoteLocalId != null && remoteLocalId != characterId) {\n"
    "                        // The server returned an EXISTING character from a different\n"
    "                        // device/install, not the one just created locally - recover\n"
    "                        // its real save instead of keeping the throwaway new one.\n"
    "                        val cloudJson = SupabaseCharacterRepository.downloadCharacterSave(supabaseCharacterId).getOrNull()\n"
    "                        if (cloudJson != null) {\n"
    "                            repository.overwriteRawJson(cloudJson)\n"
    "                            val recovered = repository.load()\n"
    "                            if (recovered != null) {\n"
    "                                recovered.accounts.forEach { accountService.restoreAccount(it) }\n"
    "                                recovered.characters.forEach { accountService.restoreCharacter(it) }\n"
    "                                recovered.skills.forEach { progressionService.restoreSkill(it) }\n"
    "                                recovered.skillingQueues.forEach { offlineIdleService.restoreSkillingQueue(it) }\n"
    "                                recovered.craftingQueues.forEach { offlineIdleService.restoreCraftingQueue(it) }\n"
    "                                recovered.lastSeen.forEach { offlineIdleService.restoreLastSeen(it) }\n"
    "                                recovered.inventoryItems.forEach { inventoryService.restoreItem(it) }\n"
    "                                recovered.equippedSlots.forEach { inventoryService.restoreEquipped(it) }\n"
    "                                recovered.loadoutSettings.forEach { inventoryService.restoreLoadoutSettings(it) }\n"
    "                                recovered.marketAccounts.forEach { marketService.restoreAccount(it) }\n"
    "                                recovered.marketOrders.forEach { marketService.restoreOrder(it) }\n"
    "                                recovered.marketPriceHistory.forEach { marketService.restorePriceHistoryEntry(it) }\n"
    "                                _currentCharacterId.value = remoteLocalId\n"
    "                                val recoveredCharacter = recovered.characters.firstOrNull { it.id == remoteLocalId }\n"
    "                                if (recoveredCharacter != null) {\n"
    "                                    _currentAccountId.value = recoveredCharacter.accountId\n"
    "                                }\n"
    "                            }\n"
    "                        }\n"
    "                    }\n"
    "                }\n"
    "            }\n"
)
assert old in content, "selectCharacter anchor not found in GameViewModel.kt"
assert content.count(old) == 1, "selectCharacter anchor not unique"
content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Patched GameViewModel.kt")

print("All 3 files patched successfully.")
