import pathlib

p = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")
text = p.read_text()

start_marker = "val debugAuthState by gameViewModel.supabaseAuthState.collectAsState()"
end_substr = "Color.Red)"

start_idx = text.find(start_marker)
if start_idx == -1:
    print("FAILED: could not find start marker")
else:
    first_end = text.find(end_substr, start_idx)
    if first_end == -1:
        print("FAILED: could not find first Color.Red) after start marker")
    else:
        first_end_full = first_end + len(end_substr)
        second_end = text.find(end_substr, first_end_full)
        if second_end == -1:
            print("FAILED: could not find second Color.Red) after the first")
        else:
            second_end_full = second_end + len(end_substr)
            segment_len = second_end_full - start_idx
            print(f"Found segment of {segment_len} chars to replace")

            replacement = '''val debugAuthState by gameViewModel.supabaseAuthState.collectAsState()
                                val debugAuthError by gameViewModel.supabaseAuthError.collectAsState()
                                val debugSupabaseCharId by gameViewModel.currentSupabaseCharacterId.collectAsState()
                                val debugCharSyncError by gameViewModel.characterSyncError.collectAsState()
                                var showDebugDialog by remember { mutableStateOf(false) }
                                LaunchedEffect(debugAuthError, debugCharSyncError) {
                                    if (debugAuthError != null || debugCharSyncError != null) {
                                        showDebugDialog = true
                                    }
                                }
                                if (showDebugDialog) {
                                    androidx.compose.material3.AlertDialog(
                                        onDismissRequest = { showDebugDialog = false },
                                        title = { androidx.compose.material3.Text("Debug: Supabase Sync") },
                                        text = {
                                            androidx.compose.foundation.layout.Column {
                                                androidx.compose.material3.Text("Auth: $debugAuthState")
                                                debugAuthError?.let { androidx.compose.material3.Text("Auth error: $it") }
                                                androidx.compose.material3.Text("Char id: ${debugSupabaseCharId ?: "none"}")
                                                debugCharSyncError?.let { androidx.compose.material3.Text("Char sync error: $it") }
                                            }
                                        },
                                        confirmButton = {
                                            androidx.compose.material3.TextButton(onClick = { showDebugDialog = false }) {
                                                androidx.compose.material3.Text("OK")
                                            }
                                        }
                                    )
                                }'''

            text = text[:start_idx] + replacement + text[second_end_full:]
            p.write_text(text)
            print("OK: replaced overlapping debug text with a dismissible dialog")
