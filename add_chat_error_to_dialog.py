import pathlib

p = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")
text = p.read_text()

anchor1 = "val debugCharSyncError by gameViewModel.characterSyncError.collectAsState()"
if text.count(anchor1) != 1:
    print(f"STEP 1 FAILED: expected 1 occurrence, found {text.count(anchor1)}")
else:
    text = text.replace(
        anchor1,
        anchor1 + "\n                                val debugChatError by gameViewModel.chatActionError.collectAsState()",
        1
    )
    print("STEP 1 OK")

anchor2 = "if (debugAuthError != null || debugCharSyncError != null) {"
if text.count(anchor2) != 1:
    print(f"STEP 2 FAILED: expected 1 occurrence, found {text.count(anchor2)}")
else:
    text = text.replace(anchor2, "if (debugAuthError != null || debugCharSyncError != null || debugChatError != null) {", 1)
    print("STEP 2 OK")

anchor3 = 'debugCharSyncError?.let { androidx.compose.material3.Text("Char sync error: $it") }'
if text.count(anchor3) != 1:
    print(f"STEP 3 FAILED: expected 1 occurrence, found {text.count(anchor3)}")
else:
    text = text.replace(
        anchor3,
        anchor3 + '\n                                                debugChatError?.let { androidx.compose.material3.Text("Chat error: $it") }',
        1
    )
    print("STEP 3 OK")

p.write_text(text)
print("DONE")
