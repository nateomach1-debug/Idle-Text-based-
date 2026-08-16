import pathlib

p = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt")
text = p.read_text()

# Exact block from refreshGuildHome() through the end of blockCharacter(),
# verbatim from the confirmed current file content.
old_block = '''    fun refreshGuildHome() {
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
        // =========================================================
    // CHAT
    // =========================================================

    private val _selectedChatChannel = MutableStateFlow(ChatChannelUi.GLOBAL)
    val selectedChatChannel: StateFlow<ChatChannelUi> = _selectedChatChannel.asStateFlow()

    private val _chatMessages = MutableStateFlow<List<ChatMessageUi>>(emptyList())
    val chatMessages: StateFlow<List<ChatMessageUi>> = _chatMessages.asStateFlow()

    private val _dmConversations = MutableStateFlow<List<DmConversationSummary>>(emptyList())
    val dmConversations: StateFlow<List<DmConversationSummary>> = _dmConversations.asStateFlow()

    private val _selectedDmCharacterId = MutableStateFlow<String?>(null)
    val selectedDmCharacterId: StateFlow<String?> = _selectedDmCharacterId.asStateFlow()

    // Not exposed as UI state - internal detail of which DM channel row
    // backs the currently selected DM conversation.
    private var selectedDmChannelId: String? = null

    private val _globalChatOptOut = MutableStateFlow(false)
    val globalChatOptOut: StateFlow<Boolean> = _globalChatOptOut.asStateFlow()

    private val _chatActionError = MutableStateFlow<String?>(null)
    val chatActionError: StateFlow<String?> = _chatActionError.asStateFlow()

    private suspend fun resolveChatChannelId(channel: ChatChannelUi): String? {
        return when (channel) {
            ChatChannelUi.GUILD -> _guildId.value?.let {
                SupabaseChatRepository.getOrCreateGuildChannel(it).getOrNull()
            }
            ChatChannelUi.DMS -> selectedDmChannelId
            else -> SupabaseChatRepository.fetchSingletonChannelId(channel)
        }
    }

    fun selectChatChannel(channel: ChatChannelUi) {
        _selectedChatChannel.value = channel
        if (channel == ChatChannelUi.DMS) {
            refreshDmConversations()
            _chatMessages.value = if (selectedDmChannelId != null) _chatMessages.value else emptyList()
        } else {
            refreshChatMessages()
        }
    }

    fun refreshChatMessages() {
        val characterId = _currentCharacterId.value ?: return
        val channel = _selectedChatChannel.value
        viewModelScope.launch {
            val channelId = resolveChatChannelId(channel)
            if (channelId == null) {
                _chatMessages.value = emptyList()
                return@launch
            }
            _chatMessages.value = SupabaseChatRepository.fetchChannelMessages(characterId, channelId, channel)
        }
    }

    fun sendChatMessage(content: String) {
        if (content.isBlank()) return
        val characterId = _currentCharacterId.value ?: return
        val channel = _selectedChatChannel.value
        viewModelScope.launch {
            val channelId = resolveChatChannelId(channel)
            if (channelId == null) {
                _chatActionError.value = "Could not resolve chat channel."
                return@launch
            }
            val result = SupabaseChatRepository.sendMessage(characterId, channelId, content)
            result.onFailure { _chatActionError.value = it.message }
            refreshChatMessages()
        }
    }

    fun refreshDmConversations() {
        val characterId = _currentCharacterId.value ?: return
        viewModelScope.launch {
            _dmConversations.value = SupabaseChatRepository.fetchDmConversations(characterId)
        }
    }

    // Also used by the MESSAGE_PLAYER chat action to jump into a DM.
    fun selectDmConversation(otherCharacterId: String) {
        val characterId = _currentCharacterId.value ?: return
        _selectedDmCharacterId.value = otherCharacterId
        viewModelScope.launch {
            val result = SupabaseChatRepository.getOrCreateDmChannel(characterId, otherCharacterId)
            result.onFailure {
                _chatActionError.value = it.message
                return@launch
            }
            selectedDmChannelId = result.getOrNull()
            refreshChatMessages()
        }
    }

    fun reportChatMessage(message: ChatMessageUi, category: String, reason: String) {
        val characterId = _currentCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseChatRepository.reportMessage(characterId, message.id, category, reason)
            result.onFailure { _chatActionError.value = it.message }
            refreshChatMessages()
        }
    }

    fun selfMuteCharacter(targetCharacterId: String) {
        val characterId = _currentCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseChatRepository.selfMute(characterId, targetCharacterId)
            result.onFailure { _chatActionError.value = it.message }
            refreshChatMessages()
        }
    }

    fun toggleGlobalChatOptOut(optOut: Boolean) {
        val characterId = _currentCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseChatRepository.setGlobalChatOptOut(characterId, optOut)
            result.onFailure {
                _chatActionError.value = it.message
                return@launch
            }
            _globalChatOptOut.value = optOut
        }
    }

    fun loadInitialChatState() {
        refreshChatMessages()
        val characterId = _currentCharacterId.value
        if (characterId != null) {
            viewModelScope.launch {
                _globalChatOptOut.value = SupabaseChatRepository.getGlobalChatOptOut(characterId)
            }
        }
    }

    fun blockCharacter(targetCharacterId: String) {
        val characterId = _currentCharacterId.value ?: return
        viewModelScope.launch {
            val result = SupabaseChatRepository.blockCharacter(characterId, targetCharacterId)
            result.onFailure { _chatActionError.value = it.message }
            refreshChatMessages()
        }
    }'''

if text.count(old_block) != 1:
    print(f"FAILED: expected 1 occurrence of the full block, found {text.count(old_block)}")
    print("Do not proceed - tell Claude so the exact text can be reconciled.")
else:
    new_block = old_block.replace("_currentCharacterId.value", "_currentSupabaseCharacterId.value")
    text = text.replace(old_block, new_block, 1)
    print("BLOCK SWAP OK: all GUILD+CHAT functions now use _currentSupabaseCharacterId")

    # Add the new StateFlow declaration itself, right before refreshGuildHome()
    anchor = "    fun refreshGuildHome() {"
    if text.count(anchor) != 1:
        print(f"STATEFLOW DECLARATION FAILED: expected 1 occurrence of anchor, found {text.count(anchor)}")
    else:
        declaration = (
            "    // The Supabase characters.id for the current character - a DIFFERENT\n"
            "    // id than _currentCharacterId (which is the local Room-database id).\n"
            "    // Every Supabase RPC call needs this one, not the local id.\n"
            "    private val _currentSupabaseCharacterId = MutableStateFlow<String?>(null)\n"
            "    val currentSupabaseCharacterId: StateFlow<String?> = _currentSupabaseCharacterId.asStateFlow()\n\n"
        )
        text = text.replace(anchor, declaration + anchor, 1)
        print("STATEFLOW DECLARATION OK: _currentSupabaseCharacterId added")

    p.write_text(text)
    print("FILE WRITTEN")
