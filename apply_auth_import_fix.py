path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(path, "r") as f:
    content = f.read()

old_import = "import kotlinx.coroutines.launch\nimport java.time.Instant\nimport kotlin.random.Random\n"
new_import = "import kotlinx.coroutines.launch\nimport java.time.Instant\nimport kotlin.random.Random\nimport io.github.jan.supabase.auth.auth\n"
assert content.count(old_import) == 1, "import anchor not found or not unique"
content = content.replace(old_import, new_import, 1)

with open(path, "w") as f:
    f.write(content)

print("OK: GameViewModel.kt patched (added missing 'auth' extension property import).")
