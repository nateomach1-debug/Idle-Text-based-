import pathlib

p = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")
text = p.read_text()

broken = 'Text("Supabase: $debugAuthState $debugErrorText", color = androidx.compose.ui.graphics.Color.Red)'
if text.count(broken) != 1:
    print(f"FAILED: expected 1 occurrence, found {text.count(broken)}")
else:
    fixed = 'androidx.compose.material3.Text("Supabase: $debugAuthState $debugErrorText", color = androidx.compose.ui.graphics.Color.Red)'
    text = text.replace(broken, fixed, 1)
    p.write_text(text)
    print("FIXED: fully-qualified the debug Text call")
