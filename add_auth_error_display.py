import pathlib

# --- GameViewModel.kt: add an error StateFlow ---
p1 = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt")
text1 = p1.read_text()

anchor1 = "    private val _supabaseAuthState = MutableStateFlow(SupabaseAuthState.SIGNED_OUT)\n    val supabaseAuthState: StateFlow<SupabaseAuthState> = _supabaseAuthState.asStateFlow()"
if text1.count(anchor1) != 1:
    print(f"STEP 1 FAILED: expected 1 occurrence, found {text1.count(anchor1)}")
else:
    text1 = text1.replace(
        anchor1,
        anchor1 + "\n\n    private val _supabaseAuthError = MutableStateFlow<String?>(null)\n    val supabaseAuthError: StateFlow<String?> = _supabaseAuthError.asStateFlow()",
        1
    )
    print("STEP 1 OK: supabaseAuthError StateFlow added")

anchor2 = "            } catch (e: Exception) {\n                _supabaseAuthState.value = SupabaseAuthState.ERROR\n            }"
if text1.count(anchor2) != 1:
    print(f"STEP 2 FAILED: expected 1 occurrence, found {text1.count(anchor2)}")
else:
    text1 = text1.replace(
        anchor2,
        "            } catch (e: Exception) {\n                _supabaseAuthState.value = SupabaseAuthState.ERROR\n                _supabaseAuthError.value = e.message ?: e.toString()\n            }",
        1
    )
    print("STEP 2 OK: real error message now captured")

p1.write_text(text1)

# --- MainActivity.kt: show it on screen ---
p2 = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")
text2 = p2.read_text()

anchor3 = "LaunchedEffect(Unit) { gameViewModel.loadInitialChatState() }"
if text2.count(anchor3) != 1:
    print(f"STEP 3 FAILED: expected 1 occurrence, found {text2.count(anchor3)}")
else:
    injection = (
        anchor3 + "\n"
        "                                val debugAuthState by gameViewModel.supabaseAuthState.collectAsState()\n"
        "                                val debugAuthError by gameViewModel.supabaseAuthError.collectAsState()\n"
        "                                Text(\"Supabase: $debugAuthState ${debugAuthError ?: \\\"\\\"}\", color = androidx.compose.ui.graphics.Color.Red)"
    )
    text2 = text2.replace(anchor3, injection, 1)
    print("STEP 3 OK: debug text added to screen")

p2.write_text(text2)
print("DONE")
