GVM = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"

with open(GVM, "r", encoding="utf-8") as f:
    content = f.read()

old = """    } catch (e: Exception) {
        return ServiceResult.Failure("No local account found, and no matching cloud account either.")
    }"""

new = """    } catch (e: Exception) {
        return ServiceResult.Failure("No local account found, and no matching cloud account either. (${e.message})")
    }"""

count = content.count(old)
assert count == 1, f"expected exactly 1 match, found {count}"
content = content.replace(old, new)

with open(GVM, "w", encoding="utf-8") as f:
    f.write(content)

print(f"OK: patched ({len(old)} -> {len(new)} chars)")
