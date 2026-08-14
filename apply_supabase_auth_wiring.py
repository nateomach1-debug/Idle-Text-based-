path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(path, "r") as f:
    content = f.read()

# --- 1. Add the Supabase auth state + background sync function, anchored right after
#         the existing combatService declaration block we added earlier (self-contained,
#         doesn't touch anything else). ---
anchor = "    // =========================================================\n    // COMBAT\n    // ========================================================="
assert content.count(anchor) == 1, "COMBAT section header not found or not unique"

supabase_auth_block = '''    // =========================================================
    // SUPABASE AUTH (guild/chat multiplayer only - local play never depends on this)
    // =========================================================

    private val _supabaseAuthState = MutableStateFlow(SupabaseAuthState.SIGNED_OUT)
    val supabaseAuthState: StateFlow<SupabaseAuthState> = _supabaseAuthState.asStateFlow()

    // Fire-and-forget: runs in the background after a successful LOCAL login/account
    // creation. If this fails (no network, Supabase down, etc.) local gameplay is
    // completely unaffected - only guild/chat multiplayer stays unavailable.
    private fun syncSupabaseAuth(email: String, password: String, isNewAccount: Boolean) {
        viewModelScope.launch {
            _supabaseAuthState.value = SupabaseAuthState.SIGNING_IN
            try {
                val auth = SupabaseClientProvider.client.auth
                if (isNewAccount) {
                    auth.signUpWith(io.github.jan.supabase.auth.providers.builtin.Email) {
                        this.email = email
                        this.password = password
                    }
                } else {
                    auth.signInWith(io.github.jan.supabase.auth.providers.builtin.Email) {
                        this.email = email
                        this.password = password
                    }
                }
                _supabaseAuthState.value = SupabaseAuthState.SIGNED_IN
            } catch (e: Exception) {
                _supabaseAuthState.value = SupabaseAuthState.ERROR
            }
        }
    }

    ''' + anchor
content = content.replace(anchor, supabase_auth_block, 1)

# --- 2. Hook the background sync call into login()'s existing success branch. ---
old_login = '''fun login(email: String, password: String): ServiceResult<Account> {
    val result = accountService.login(email, password)
    if (result is ServiceResult.Success) {
        sessionManager.saveSession(result.value.id)
            _currentAccountId.value = result.value.id
            refreshCurrency()
    }
    return result
}'''
new_login = '''fun login(email: String, password: String): ServiceResult<Account> {
    val result = accountService.login(email, password)
    if (result is ServiceResult.Success) {
        sessionManager.saveSession(result.value.id)
            _currentAccountId.value = result.value.id
            refreshCurrency()
            syncSupabaseAuth(email, password, isNewAccount = false)
    }
    return result
}'''
assert content.count(old_login) == 1, "login() block not found or not unique"
content = content.replace(old_login, new_login, 1)

# --- 3. Hook the background sync call into createAccount()'s existing success branch. ---
old_create = '''  fun createAccount(email: String, username: String, password: String): ServiceResult<Account> {
    val result = accountService.createAccount(email, username, password, AgeBracket.ADULT_18_PLUS, "US")
    if (result is ServiceResult.Success) {
        sessionManager.saveSession(result.value.id)
            _currentAccountId.value = result.value.id
            refreshCurrency()
    }
    return result
  }'''
new_create = '''  fun createAccount(email: String, username: String, password: String): ServiceResult<Account> {
    val result = accountService.createAccount(email, username, password, AgeBracket.ADULT_18_PLUS, "US")
    if (result is ServiceResult.Success) {
        sessionManager.saveSession(result.value.id)
            _currentAccountId.value = result.value.id
            refreshCurrency()
            syncSupabaseAuth(email, password, isNewAccount = true)
    }
    return result
  }'''
assert content.count(old_create) == 1, "createAccount() block not found or not unique"
content = content.replace(old_create, new_create, 1)

with open(path, "w") as f:
    f.write(content)

print("OK: GameViewModel.kt patched (Supabase auth state added, hooked into login()/createAccount() as a non-blocking background call).")
