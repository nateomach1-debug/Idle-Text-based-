path = "app/src/main/kotlin/com/yourname/idlerpg/ChatBanner.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor = '''            LazyColumn(modifier = Modifier.weight(1f)) {
                items(messages) { msg ->
                    ChatMessageRow(msg, onMessageAction)
                }
            }'''
count = content.count(anchor)
assert count == 1, f"Expected 1 match, found {count}."
replacement = '''            LazyColumn(modifier = Modifier.weight(1f)) {
                items(messages.reversed()) { msg ->
                    ChatMessageRow(msg, onMessageAction)
                }
            }'''
content = content.replace(anchor, replacement, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("patch_expanded_chat_newest_first.py applied cleanly.")
