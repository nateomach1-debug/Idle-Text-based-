def apply(content, old, new, label):
    count = content.count(old)
    if count != 1:
        raise SystemExit(f"FAILED [{label}]: expected 1 match, found {count}")
    return content.replace(old, new, 1)

GVM_PATH = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(GVM_PATH, "r", encoding="utf-8") as f:
    gvm = f.read()

gvm = apply(gvm,
"""    fun refreshGuildHome() {
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            val membership = SupabaseGuildRepository.findMembership(characterId)
            _guildId.value = membership?.first
            if (membership == null) {
                _guildHomeState.value = null
                _guildLeaderboard.value = emptyList()
                _browsableGuilds.value = SupabaseGuildRepository.listGuilds()
            } else {
                SupabaseGuildRepository.closeExpiredGuildEventIfNeeded(membership.first)
                _guildHomeState.value = SupabaseGuildRepository.fetchGuildHome(characterId)
                _guildLeaderboard.value = SupabaseGuildRepository.fetchLeaderboard(characterId)
                claimGuildEventPayouts()
            }
        }
    }""",
"""    fun refreshGuildHome() {
        val characterId = _currentSupabaseCharacterId.value ?: return
        viewModelScope.launch {
            try {
                val membership = SupabaseGuildRepository.findMembership(characterId)
                _guildId.value = membership?.first
                if (membership == null) {
                    _guildHomeState.value = null
                    _guildLeaderboard.value = emptyList()
                    _browsableGuilds.value = SupabaseGuildRepository.listGuilds()
                } else {
                    SupabaseGuildRepository.closeExpiredGuildEventIfNeeded(membership.first)
                    _guildHomeState.value = SupabaseGuildRepository.fetchGuildHome(characterId)
                    _guildLeaderboard.value = SupabaseGuildRepository.fetchLeaderboard(characterId)
                    claimGuildEventPayouts()
                }
            } catch (e: Exception) {
                // Temporary diagnostic: fetchGuildHome() previously had no error
                // surfacing at all, so any exception (e.g. a date-parsing or
                // decode failure) silently left stale state in place with no
                // visible sign anything went wrong.
                _guildActionError.value = "refreshGuildHome failed: " + (e.message ?: e.toString())
            }
        }
    }""",
    "refreshGuildHome: surface exceptions instead of silently swallowing them"
)

with open(GVM_PATH, "w", encoding="utf-8") as f:
    f.write(gvm)

print("Applied successfully.")
