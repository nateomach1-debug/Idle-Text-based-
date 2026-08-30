# patch_fix_service_result_field_name.py
path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor = "stoppedReason = (result as? ServiceResult.Failure)?.message ?: \"Missing materials or requirements.\""
count = content.count(anchor)
assert count == 1, f"Expected 1 match, found {count}."
replacement = "stoppedReason = (result as? ServiceResult.Failure)?.reason ?: \"Missing materials or requirements.\""
content = content.replace(anchor, replacement, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("patch_fix_service_result_field_name.py applied cleanly.")
