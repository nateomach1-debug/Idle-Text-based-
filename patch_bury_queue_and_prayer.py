def apply(content, old, new, label):
    count = content.count(old)
    if count != 1:
        raise SystemExit(f"FAILED [{label}]: expected 1 match, found {count}")
    return content.replace(old, new, 1)

SGR_PATH = "app/src/main/kotlin/com/yourname/idlerpg/SupabaseGuildRepository.kt"
with open(SGR_PATH, "r", encoding="utf-8") as f:
    sgr = f.read()

sgr = apply(sgr,
"""    // TEMPORARY diagnostic field - remove once the missing-event issue is found.
    var lastEventDebug: String = 

    // Finds which guild (if any) a character belongs to, and their role in it.""",
"""    // TEMPORARY diagnostic field - remove once the missing-event issue is found.
    var lastEventDebug: String = ""

    // Finds which guild (if any) a character belongs to, and their role in it.""",
    "fix: restore missing empty-string initializer for lastEventDebug"
)

with open(SGR_PATH, "w", encoding="utf-8") as f:
    f.write(sgr)

print("Fixed.")
