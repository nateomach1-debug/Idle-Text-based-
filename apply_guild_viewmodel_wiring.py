path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(path, "r") as f:
    content = f.read()

anchor = "    // =========================================================\n    // COMBAT\n    // ========================================================="
assert content.count(anchor) == 1, "COMBAT section header not found or not unique"

guild_block = '''    // =========================================================
    // GUILD (Supabase-backed, best-effort - local play never depends on this)
    // =========================================================

    private val _guildHomeState = MutableStateFlow<GuildHomeState?>(null)
    val guildHomeState: StateFlow<GuildHomeState?> = _guildHomeState.asStateFlow()

    private val _guildId = MutableStateFlow<String?>(null)

    private val _guildLeaderboard = MutableStateFlow<List<GuildLeaderboardEntry>>(emptyList())
    val guildLeaderboard: StateFlow<List<GuildLeaderboardEntry>> = _guildLeaderboard.asStateFlow()

    private val _browsableGuilds = MutableStateFlow<List<GuildBrowseEntry>>(emptyList())
    val browsableGuilds: StateFlow<List<GuildBrowseEntry>> = _browsableGuilds.asStateFlow()

    private val _guildActionError = MutableStateFlow<String?>(null)
    val guildActionError: StateFlow<String?> = _guildActionError.asStateFlow()

    fun refreshGuildHome() {
        val characterId = _currentCharacterId.value ?: return
        viewModelScope.launch {
            val membership = SupabaseGuildRepository.findMembership(characterId)
            _guildId.value = membership?.first
            if (membership == null) {
                _guildHomeState.value = null
                _guildLeaderboard.value = emptyList()
                _browsableGuilds.value = SupabaseGuildRepository.listGuilds()
            } else {
                _guildHomeState.value = SupabaseGuildRepository.fetchGuildHome(characterId)
                _guildLeaderboard.value = SupabaseGuildRepository.fetchLeaderboard(characterId)
            }
        }
    }

    fun createGuild(name: String) {
        val characterId = _currentCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseGuildRepository.createGuild(name, characterId)
            result.onFailure { _guildActionError.value = it.message }
            refreshGuildHome()
        }
    }

    fun joinGuild(guildId: String) {
        val characterId = _currentCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseGuildRepository.joinGuild(guildId, characterId)
            result.onFailure { _guildActionError.value = it.message }
            refreshGuildHome()
        }
    }

    fun kickGuildMember(targetCharacterId: String) {
        val guildId = _guildId.value ?: return
        val characterId = _currentCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseGuildRepository.kickMember(guildId, characterId, targetCharacterId)
            result.onFailure { _guildActionError.value = it.message }
            refreshGuildHome()
        }
    }

    fun promoteGuildMemberToOfficer(targetCharacterId: String) {
        val guildId = _guildId.value ?: return
        val characterId = _currentCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseGuildRepository.promoteToOfficer(guildId, characterId, targetCharacterId)
            result.onFailure { _guildActionError.value = it.message }
            refreshGuildHome()
        }
    }

    fun promoteGuildMemberToLeader(targetCharacterId: String) {
        val guildId = _guildId.value ?: return
        val characterId = _currentCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseGuildRepository.promoteToLeader(guildId, characterId, targetCharacterId)
            result.onFailure { _guildActionError.value = it.message }
            refreshGuildHome()
        }
    }

    ''' + anchor
content = content.replace(anchor, guild_block, 1)

with open(path, "w") as f:
    f.write(content)

print("OK: GameViewModel.kt patched (guild state flows + action functions added).")
