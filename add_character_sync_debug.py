import pathlib

# --- GameViewModel.kt: add error state + capture failures ---
p1 = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt")
text1 = p1.read_text()

anchor1 = "    private val _currentSupabaseCharacterId = MutableStateFlow<String?>(null)\n    val currentSupabaseCharacterId: StateFlow<String?> = _currentSupabaseCharacterId.asStateFlow()"
if text1.count(anchor1) != 1:
    print(f"STEP 1 FAILED: expected 1 occurrence, found {text1.count(anchor1)}")
else:
    text1 = text1.replace(
        anchor1,
        anchor1 + "\n\n    private val _characterSyncError = MutableStateFlow<String?>(null)\n    val characterSyncError: StateFlow<String?> = _characterSyncError.asStateFlow()",
        1
    )
    print("STEP 1 OK: characterSyncError state added")

anchor2 = """        val selectedCharacter = accountService.charactersFor(_currentAccountId.value ?: "").firstOrNull { it.id == characterId }
        if (selectedCharacter != null) {
            viewModelScope.launch {
                val result = SupabaseCharacterRepository.getOrCreateCharacter(characterId, selectedCharacter.displayName)
                _currentSupabaseCharacterId.value = result.getOrNull()
            }
        }"""
if text1.count(anchor2) != 1:
    print(f"STEP 2 FAILED: expected 1 occurrence, found {text1.count(anchor2)}")
else:
    replacement = """        val selectedCharacter = accountService.charactersFor(_currentAccountId.value ?: "").firstOrNull { it.id == characterId }
        if (selectedCharacter != null) {
            viewModelScope.launch {
                val result = SupabaseCharacterRepository.getOrCreateCharacter(characterId, selectedCharacter.displayName)
                result.onFailure { _characterSyncError.value = it.message ?: it.toString() }
                result.onSuccess { _characterSyncError.value = null }
                _currentSupabaseCharacterId.value = result.getOrNull()
            }
        } else {
            _characterSyncError.value = "selectedCharacter was null - accountId=${_currentAccountId.value}, characterId=$characterId"
        }"""
    text1 = text1.replace(anchor2, replacement, 1)
    print("STEP 2 OK: failures now captured, including the 'character not found in account list' case")

p1.write_text(text1)

# --- MainActivity.kt: show it alongside the existing auth debug text ---
p2 = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")
text2 = p2.read_text()

anchor3 = 'androidx.compose.material3.Text("Supabase: $debugAuthState $debugErrorText", color = androidx.compose.ui.graphics.Color.Red)'
if text2.count(anchor3) != 1:
    print(f"STEP 3 FAILED: expected 1 occurrence, found {text2.count(anchor3)}")
else:
    injection = (
        anchor3 + "\n"
        "                                val debugSupabaseCharId by gameViewModel.currentSupabaseCharacterId.collectAsState()\n"
        "                                val debugCharSyncError by gameViewModel.characterSyncError.collectAsState()\n"
        "                                val debugCharErrorText = debugCharSyncError ?: \"\"\n"
        "                                androidx.compose.material3.Text(\"CharSync: $debugSupabaseCharId $debugCharErrorText\", color = androidx.compose.ui.graphics.Color.Red)"
    )
    text2 = text2.replace(anchor3, injection, 1)
    print("STEP 4 OK: character sync debug text added")

p2.write_text(text2)
print("DONE")
