import pathlib

p = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt")
text = p.read_text()

# Add the import
anchor_import = "package com.yourname.idlerpg\n"
if text.count(anchor_import) != 1:
    print(f"IMPORT FAILED: expected 1 occurrence, found {text.count(anchor_import)}")
else:
    text = text.replace(
        anchor_import,
        anchor_import + "\nimport io.github.jan.supabase.auth.status.SessionStatus\n",
        1
    )
    print("IMPORT OK")

# Add the new init block right before onCleared()
anchor_init = "override fun onCleared() {"
if text.count(anchor_init) != 1:
    print(f"INIT BLOCK FAILED: expected 1 occurrence, found {text.count(anchor_init)}")
else:
    new_init = '''init {
        viewModelScope.launch {
            SupabaseClientProvider.client.auth.sessionStatus.collect { status ->
                when (status) {
                    is SessionStatus.Authenticated -> {
                        _supabaseAuthState.value = SupabaseAuthState.SIGNED_IN
                        _supabaseAuthError.value = null
                    }
                    is SessionStatus.NotAuthenticated -> {
                        _supabaseAuthState.value = SupabaseAuthState.SIGNED_OUT
                    }
                    else -> {
                        // Covers Initializing/LoadingFromStorage and RefreshFailure,
                        // whichever names this supabase-kt version uses - all transient.
                        _supabaseAuthState.value = SupabaseAuthState.SIGNING_IN
                    }
                }
            }
        }
    }

    '''
    text = text.replace(anchor_init, new_init + anchor_init, 1)
    print("INIT BLOCK OK")

p.write_text(text)
print("DONE")
