import pathlib

p = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt")
text = p.read_text()

start_marker = "fun refreshGuildHome() {"
end_marker = "// COMBAT"

start_idx = text.find(start_marker)
if start_idx == -1:
    print("FAILED: could not find start marker 'fun refreshGuildHome() {'")
else:
    end_idx = text.find(end_marker, start_idx)
    if end_idx == -1:
        print("FAILED: could not find end marker '// COMBAT' after the start marker")
    else:
        segment = text[start_idx:end_idx]
        occurrences = segment.count("_currentCharacterId.value")
        print(f"Found segment of {len(segment)} chars, {occurrences} occurrences of '_currentCharacterId.value'")
        if occurrences == 0:
            print("FAILED: no occurrences found in segment - something is wrong, do not proceed")
        else:
            new_segment = segment.replace("_currentCharacterId.value", "_currentSupabaseCharacterId.value")
            text = text[:start_idx] + new_segment + text[end_idx:]

            # Add the new StateFlow declaration right before the start marker
            declaration = (
                "// The Supabase characters.id for the current character - a DIFFERENT\n"
                "    // id than _currentCharacterId (which is the local Room-database id).\n"
                "    // Every Supabase RPC call needs this one, not the local id.\n"
                "    private val _currentSupabaseCharacterId = MutableStateFlow<String?>(null)\n"
                "    val currentSupabaseCharacterId: StateFlow<String?> = _currentSupabaseCharacterId.asStateFlow()\n\n    "
            )
            insert_idx = text.find(start_marker)
            text = text[:insert_idx] + declaration + text[insert_idx:]

            p.write_text(text)
            print(f"OK: replaced {occurrences} occurrences and added _currentSupabaseCharacterId declaration")
