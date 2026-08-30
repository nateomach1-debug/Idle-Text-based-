path = "app/src/main/kotlin/com/yourname/idlerpg/ChatBanner.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor = "            CollapsedMessagePreview(messages.takeLast(3))"
count = content.count(anchor)
assert count == 1, f"Expected 1 match, found {count}."
replacement = "            CollapsedMessagePreview(messages.takeLast(3).reversed())"
content = content.replace(anchor, replacement, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("patch_collapsed_chat_newest_first.py applied cleanly.")
