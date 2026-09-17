import sys

BASE = "app/src/main/kotlin/com/yourname/idlerpg/"
MODERATION_REPO = BASE + "SupabaseModerationRepository.kt"
GAME_VIEW_MODEL = BASE + "GameViewModel.kt"
MODERATION_SCREEN = BASE + "ModerationScreen.kt"
MAIN_ACTIVITY = BASE + "MainActivity.kt"


def guarded_replace(path, old, new, label):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    if new in text:
        print(f"SKIP (already applied): {label} ({path})")
        return True

    count = text.count(old)
    if count == 1:
        text = text.replace(old, new)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"OK: {label} ({path})")
        return True
    elif count == 0:
        print(f"FAIL (old_str not found, new_str not found either): {label} ({path})")
        return False
    else:
        print(f"FAIL (old_str matched {count} times, expected 1): {label} ({path})")
        return False


def check_braces(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    opens = text.count("{")
    closes = text.count("}")
    ok = opens == closes
    print(f"{'Brace check OK' if ok else 'WARNING: brace mismatch'}: {path} ({{ = {opens}, }} = {closes})")
    return ok


results = []

# ===========================================================
# 1. SupabaseModerationRepository.kt - add findCharacterIdByName
# ===========================================================
old = '''    // ---------------------------------------------------------
    // PREMIUM CURRENCY (GEMS) - MODERATOR GRANT
    // ---------------------------------------------------------

    suspend fun grantGems(characterId: String, amount: Long, reason: String): Result<Long> = runCatching {
        client.postgrest.rpc("admin_grant_gems", buildJsonObject {
            put("p_character_id", characterId)
            put("p_amount", amount)
            put("p_reason", reason)
        }).decodeAs<Long>()
    }
}'''
new = '''    // ---------------------------------------------------------
    // PREMIUM CURRENCY (GEMS) - MODERATOR GRANT
    // ---------------------------------------------------------

    suspend fun grantGems(characterId: String, amount: Long, reason: String): Result<Long> = runCatching {
        client.postgrest.rpc("admin_grant_gems", buildJsonObject {
            put("p_character_id", characterId)
            put("p_amount", amount)
            put("p_reason", reason)
        }).decodeAs<Long>()
    }

    // ---------------------------------------------------------
    // CHARACTER LOOKUP BY DISPLAY NAME
    // Moderators only ever see a player's display_name (the name
    // shown in chat), never their raw character id - this resolves
    // one to the other so the manual mute/grant tools can take the
    // name a moderator actually has.
    // ---------------------------------------------------------

    suspend fun findCharacterIdByName(displayName: String): Result<String> = runCatching {
        client.postgrest.rpc("admin_find_character_id", buildJsonObject {
            put("p_display_name", displayName)
        }).decodeAs<String>()
    }
}'''
results.append(guarded_replace(MODERATION_REPO, old, new, "SupabaseModerationRepository.kt findCharacterIdByName"))

# ===========================================================
# 2. GameViewModel.kt - lookup error state + by-name moderator wrappers
# ===========================================================
old = '''    fun refreshModeration() {
        if (!_isModerator.value) return
        viewModelScope.launch {
            _moderationState.value = _moderationState.value.copy(isLoading = true)
            val reports = SupabaseModerationRepository.fetchPendingReports()
            val appeals = SupabaseModerationRepository.fetchPendingAppeals()
            _moderationState.value = ModerationState(reports, appeals, isLoading = false)
        }
    }

    fun resolveReport(reportId: String, actionTaken: Boolean) {'''
new = '''    fun refreshModeration() {
        if (!_isModerator.value) return
        viewModelScope.launch {
            _moderationState.value = _moderationState.value.copy(isLoading = true)
            val reports = SupabaseModerationRepository.fetchPendingReports()
            val appeals = SupabaseModerationRepository.fetchPendingAppeals()
            _moderationState.value = ModerationState(reports, appeals, isLoading = false)
        }
    }

    private val _moderationLookupError = MutableStateFlow<String?>(null)
    val moderationLookupError: StateFlow<String?> = _moderationLookupError.asStateFlow()

    // Moderator convenience - resolves a display name (the name shown in
    // chat) to its Supabase character id via admin_find_character_id, then
    // delegates to the existing mute/unmute/grant RPCs directly. A failed
    // lookup (typo, no such name) surfaces in moderationLookupError instead
    // of silently doing nothing.
    fun muteCharacterByNameAsModerator(displayName: String, durationSeconds: Int, reason: String) {
        viewModelScope.launch {
            _moderationLookupError.value = null
            val idResult = SupabaseModerationRepository.findCharacterIdByName(displayName)
            idResult.onFailure { _moderationLookupError.value = it.message ?: it.toString() }
            idResult.onSuccess { characterId ->
                SupabaseModerationRepository.muteCharacter(characterId, durationSeconds, reason)
            }
        }
    }

    fun unmuteCharacterByNameAsModerator(displayName: String) {
        viewModelScope.launch {
            _moderationLookupError.value = null
            val idResult = SupabaseModerationRepository.findCharacterIdByName(displayName)
            idResult.onFailure { _moderationLookupError.value = it.message ?: it.toString() }
            idResult.onSuccess { characterId ->
                SupabaseModerationRepository.unmuteCharacter(characterId)
            }
        }
    }

    fun grantGemsByNameAsModerator(displayName: String, amount: Long, reason: String) {
        viewModelScope.launch {
            _moderationLookupError.value = null
            val idResult = SupabaseModerationRepository.findCharacterIdByName(displayName)
            idResult.onFailure { _moderationLookupError.value = it.message ?: it.toString() }
            idResult.onSuccess { characterId ->
                SupabaseModerationRepository.grantGems(characterId, amount, reason)
            }
        }
    }

    fun resolveReport(reportId: String, actionTaken: Boolean) {'''
results.append(guarded_replace(GAME_VIEW_MODEL, old, new, "GameViewModel.kt by-name moderator wrappers + lookup error state"))

# ===========================================================
# 3. ModerationScreen.kt - lookupError param + display, relabel fields
# ===========================================================
old = '''@Composable
fun ModerationScreen(
    state: ModerationState,
    onResolveReport: (reportId: String, actionTaken: Boolean) -> Unit,
    onResolveAppeal: (appealId: String, grant: Boolean, notes: String) -> Unit,
    onMuteCharacter: (characterId: String, durationSeconds: Int, reason: String) -> Unit,
    onUnmuteCharacter: (characterId: String) -> Unit,
    onGrantGems: (String, Long, String) -> Unit = { _, _, _ -> },
    modifier: Modifier = Modifier
) {
    val scrollState = rememberScrollState()

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(20.dp)
            .verticalScroll(scrollState)
    ) {
        Text(
            text = "Moderation",
            style = MaterialTheme.typography.headlineMedium,
            textAlign = TextAlign.Center,
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(16.dp))'''
new = '''@Composable
fun ModerationScreen(
    state: ModerationState,
    onResolveReport: (reportId: String, actionTaken: Boolean) -> Unit,
    onResolveAppeal: (appealId: String, grant: Boolean, notes: String) -> Unit,
    onMuteCharacter: (characterId: String, durationSeconds: Int, reason: String) -> Unit,
    onUnmuteCharacter: (characterId: String) -> Unit,
    onGrantGems: (String, Long, String) -> Unit = { _, _, _ -> },
    lookupError: String? = null,
    modifier: Modifier = Modifier
) {
    val scrollState = rememberScrollState()

    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(20.dp)
            .verticalScroll(scrollState)
    ) {
        Text(
            text = "Moderation",
            style = MaterialTheme.typography.headlineMedium,
            textAlign = TextAlign.Center,
            modifier = Modifier.fillMaxWidth()
        )

        if (lookupError != null) {
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = lookupError,
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodyMedium
            )
        }

        Spacer(modifier = Modifier.height(16.dp))'''
results.append(guarded_replace(MODERATION_SCREEN, old, new, "ModerationScreen.kt lookupError param + display"))

old = '''        Text(text = "Grant Gems", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = characterId,
            onValueChange = { characterId = it },
            label = { Text(text = "Character ID") },
            modifier = Modifier.fillMaxWidth()
        )'''
new = '''        Text(text = "Grant Gems", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = characterId,
            onValueChange = { characterId = it },
            label = { Text(text = "Character Name") },
            modifier = Modifier.fillMaxWidth()
        )'''
results.append(guarded_replace(MODERATION_SCREEN, old, new, "ModerationScreen.kt relabel Grant Gems field"))

old = '''        Text(text = "Manual Mute", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = characterId,
            onValueChange = { characterId = it },
            label = { Text(text = "Character ID") },
            modifier = Modifier.fillMaxWidth()
        )'''
new = '''        Text(text = "Manual Mute", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = characterId,
            onValueChange = { characterId = it },
            label = { Text(text = "Character Name") },
            modifier = Modifier.fillMaxWidth()
        )'''
results.append(guarded_replace(MODERATION_SCREEN, old, new, "ModerationScreen.kt relabel Manual Mute field"))

# ===========================================================
# 4. MainActivity.kt - rewire callbacks to by-name functions, pass lookupError
# ===========================================================
old = '''                                ModerationScreen(
                                    state = moderation,
                                    onResolveReport = { id, action -> gameViewModel.resolveReport(id, action) },
                                    onResolveAppeal = { id, grant, notes -> gameViewModel.resolveAppeal(id, grant, notes) },
                                    onMuteCharacter = { id, dur, reason -> gameViewModel.muteCharacterAsModerator(id, dur, reason) },
                                    onUnmuteCharacter = { id -> gameViewModel.unmuteCharacterAsModerator(id) },
                                    onGrantGems = { id, amount, reason -> gameViewModel.grantGemsAsModerator(id, amount, reason) }
                                )'''
new = '''                                val moderationLookupError by gameViewModel.moderationLookupError.collectAsState()
                                ModerationScreen(
                                    state = moderation,
                                    onResolveReport = { id, action -> gameViewModel.resolveReport(id, action) },
                                    onResolveAppeal = { id, grant, notes -> gameViewModel.resolveAppeal(id, grant, notes) },
                                    onMuteCharacter = { name, dur, reason -> gameViewModel.muteCharacterByNameAsModerator(name, dur, reason) },
                                    onUnmuteCharacter = { name -> gameViewModel.unmuteCharacterByNameAsModerator(name) },
                                    onGrantGems = { name, amount, reason -> gameViewModel.grantGemsByNameAsModerator(name, amount, reason) },
                                    lookupError = moderationLookupError
                                )'''
results.append(guarded_replace(MAIN_ACTIVITY, old, new, "MainActivity.kt rewire moderation callbacks to by-name"))

print()
print("=== Brace balance check ===")
for p in [MODERATION_REPO, GAME_VIEW_MODEL, MODERATION_SCREEN, MAIN_ACTIVITY]:
    check_braces(p)

if not all(results):
    print()
    print("One or more edits FAILED - review output above before committing.")
    sys.exit(1)

print()
print("All edits applied successfully.")
