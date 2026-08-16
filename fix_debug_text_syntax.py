import pathlib

p = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")
text = p.read_text()

broken = 'Text("Supabase: $debugAuthState ${debugAuthError ?: \\"\\"}", color = androidx.compose.ui.graphics.Color.Red)'
if text.count(broken) != 1:
    print(f"FAILED: expected 1 occurrence of broken text, found {text.count(broken)}")
    print("Searching for a close match instead...")
    idx = text.find('Text("Supabase:')
    if idx == -1:
        print("Could not find the debug Text call at all - tell Claude")
    else:
        print("Found nearby text, but not an exact match:")
        print(repr(text[idx-20:idx+180]))
else:
    fixed = (
        'val debugErrorText = debugAuthError ?: ""\n'
        '                                Text("Supabase: $debugAuthState $debugErrorText", color = androidx.compose.ui.graphics.Color.Red)'
    )
    text = text.replace(broken, fixed, 1)
    p.write_text(text)
    print("FIXED: replaced broken debug Text call with safe version")
