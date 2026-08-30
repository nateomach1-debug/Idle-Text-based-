path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor = '''                // Only one of these ever fires per selection: whichever character id
                // turned out to be correct once the async cloud-recovery check above
                // finished. Previously an immediate, unconditional call fired outside
                // this coroutine entirely, racing this check - it would briefly show
                // an offline-progress popup built from the wrong (pre-recovery)
                // character before this corrected one silently replaced it.
                resolveOfflineRewardsAndSync(recoveredToRemoteId ?: characterId)'''
count = content.count(anchor)
assert count == 1, f"Expected 1 match, found {count}."
replacement = '''                // Only one of these ever fires per selection: whichever character id
                // turned out to be correct once the async cloud-recovery check above
                // finished. Previously an immediate, unconditional call fired outside
                // this coroutine entirely, racing this check - it would briefly show
                // an offline-progress popup built from the wrong (pre-recovery)
                // character before this corrected one silently replaced it.
                resolveOfflineRewardsAndSync(recoveredToRemoteId ?: characterId)
                // Prefetch guild/chat data now (a live signed-in session is
                // guaranteed at this point) instead of waiting for the user to
                // visit the Guild tab, where these previously only started
                // fetching on first navigation - making the network round trip
                // visible every time instead of already being warm.
                refreshGuildHome()
                loadInitialChatState()'''
content = content.replace(anchor, replacement, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("patch_prefetch_guild_and_chat.py applied cleanly.")
