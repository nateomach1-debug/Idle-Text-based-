import pathlib

p = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt")
text = p.read_text()

anchor = "package com.yourname.idlerpg.data\n"
if text.count(anchor) != 1:
    print(f"FAILED: expected 1 occurrence, found {text.count(anchor)}")
else:
    text = text.replace(anchor, anchor + "\nimport io.github.jan.supabase.auth.status.SessionStatus\n", 1)
    p.write_text(text)
    print("OK: import added")
