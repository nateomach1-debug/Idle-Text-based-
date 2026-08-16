import pathlib

p = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")
text = p.read_text()
original = text

# Fix 1: call loadInitialChatState() alongside the existing guild-home load
anchor1 = "LaunchedEffect(Unit) { gameViewModel.refreshGuildHome() }"
if text.count(anchor1) != 1:
    print(f"FIX 1 FAILED: expected 1 occurrence of anchor, found {text.count(anchor1)}")
else:
    text = text.replace(
        anchor1,
        anchor1 + "\n                                LaunchedEffect(Unit) { gameViewModel.loadInitialChatState() }",
        1
    )
    print("FIX 1 OK: loadInitialChatState() call added")

# Fix 2a: hook REPORT action to open a dialog instead of hardcoding category/reason
anchor2 = 'ChatMessageAction.REPORT -> gameViewModel.reportChatMessage(message, "OTHER", "Reported from chat")'
if text.count(anchor2) != 1:
    print(f"FIX 2a FAILED: expected 1 occurrence of anchor, found {text.count(anchor2)}")
else:
    text = text.replace(anchor2, "ChatMessageAction.REPORT -> reportDialogMessage = message", 1)
    print("FIX 2a OK: REPORT action now opens dialog")

# Fix 2b: declare dialog state + render the dialog, right before the ChatBanner call
anchor3 = "ChatBanner("
if text.count(anchor3) != 1:
    print(f"FIX 2b FAILED: expected 1 occurrence of anchor, found {text.count(anchor3)}")
else:
    injection = (
        "var reportDialogMessage by remember { mutableStateOf<ChatMessageUi?>(null) }\n"
        "                    reportDialogMessage?.let { targetMessage ->\n"
        "                        ReportMessageDialog(\n"
        "                            message = targetMessage,\n"
        "                            onDismiss = { reportDialogMessage = null },\n"
        "                            onSubmit = { category, reason ->\n"
        "                                gameViewModel.reportChatMessage(targetMessage, category, reason)\n"
        "                                reportDialogMessage = null\n"
        "                            }\n"
        "                        )\n"
        "                    }\n\n"
        "                    ChatBanner("
    )
    text = text.replace(anchor3, injection, 1)
    print("FIX 2b OK: report dialog state + render added before ChatBanner call")

# Add the import for ReportMessageDialog, right after the package line
anchor4 = "package com.yourname.idlerpg\n"
if text.count(anchor4) != 1:
    print(f"IMPORT FAILED: expected 1 occurrence of package line, found {text.count(anchor4)}")
else:
    text = text.replace(anchor4, anchor4 + "\nimport com.yourname.idlerpg.ui.components.ReportMessageDialog\n", 1)
    print("IMPORT OK: ReportMessageDialog import added")

if text != original:
    p.write_text(text)
    print("FILE WRITTEN")
else:
    print("NO CHANGES WRITTEN - check failures above")
