import pathlib

p = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt")
text = p.read_text()

anchor = """    fun selectCharacter(characterId: String) {
        _currentCharacterId.value = characterId
"""

if text.count(anchor) != 1:
    print(f"FAILED: expected 1 occurrence, found {text.count(anchor)}")
else:
    injection = """
        val selectedCharacter = accountService.charactersFor(_currentAccountId.value ?: "").firstOrNull { it.id == characterId }
        if (selectedCharacter != null) {
            viewModelScope.launch {
                val result = SupabaseCharacterRepository.getOrCreateCharacter(characterId, selectedCharacter.displayName)
                _currentSupabaseCharacterId.value = result.getOrNull()
            }
        }
"""
    text = text.replace(anchor, anchor + injection, 1)
    p.write_text(text)
    print("OK: character sync wired into selectCharacter()")
