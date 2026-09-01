# PART M: Completion notification for finishing a bury queue's full target
# (reuses the existing ActionStoppedNotice dialog, but the "Ran out of
# materials for X" wording was hardcoded for the failure case - added an
# isCompletion flag so it can show a proper success message instead).

gvm_path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(gvm_path, encoding="utf-8") as f:
    content = f.read()

anchor_notice_class = "    data class ActionStoppedNotice(val itemName: String, val reason: String)"
count = content.count(anchor_notice_class)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(
    anchor_notice_class,
    "    data class ActionStoppedNotice(val itemName: String, val reason: String, val isCompletion: Boolean = false)",
    1
)

anchor_tick_complete = '''        if (queue.isTargetReached()) {
            offlineIdleService.stopQueue(characterId)
            buryActionProgressSeconds = 0
            refreshActiveQueue()
        } else if (effectiveAttempts < cappedAttempts) {'''
count2 = content.count(anchor_tick_complete)
assert count2 == 1, f"Expected 1 match, found {count2}."
replacement_tick_complete = '''        if (queue.isTargetReached()) {
            offlineIdleService.stopQueue(characterId)
            buryActionProgressSeconds = 0
            refreshActiveQueue()
            _actionStoppedNotifications.value = _actionStoppedNotifications.value + ActionStoppedNotice(
                itemName = formatItemName(queue.itemId),
                reason = "Buried " + queue.quantityCompleted + "x " + formatItemName(queue.itemId) +
                    " (+" + (queue.quantityCompleted * boneInfo.xpAmount) + " Prayer XP).",
                isCompletion = true
            )
        } else if (effectiveAttempts < cappedAttempts) {'''
content = content.replace(anchor_tick_complete, replacement_tick_complete, 1)

with open(gvm_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part M (1/2 - GameViewModel.kt) applied cleanly.")

# Update the dialog rendering to branch on isCompletion.
main_path = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
with open(main_path, encoding="utf-8") as f:
    content = f.read()

anchor_dialog = '''    val actionStoppedNotifications by gameViewModel.actionStoppedNotifications.collectAsState()
    actionStoppedNotifications.firstOrNull()?.let { notice ->
        androidx.compose.material3.AlertDialog(
            onDismissRequest = { gameViewModel.dismissActionStoppedNotification() },
            title = { androidx.compose.material3.Text("Action Stopped") },
            text = {
                androidx.compose.material3.Text(
                    "Ran out of materials for " + notice.itemName + ".\\n" + notice.reason
                )
            },
            confirmButton = {
                androidx.compose.material3.TextButton(onClick = { gameViewModel.dismissActionStoppedNotification() }) {
                    androidx.compose.material3.Text("OK")
                }
            }
        )
    }'''
count3 = content.count(anchor_dialog)
assert count3 == 1, f"Expected 1 match, found {count3}."
replacement_dialog = '''    val actionStoppedNotifications by gameViewModel.actionStoppedNotifications.collectAsState()
    actionStoppedNotifications.firstOrNull()?.let { notice ->
        androidx.compose.material3.AlertDialog(
            onDismissRequest = { gameViewModel.dismissActionStoppedNotification() },
            title = { androidx.compose.material3.Text(if (notice.isCompletion) "Done!" else "Action Stopped") },
            text = {
                androidx.compose.material3.Text(
                    if (notice.isCompletion) {
                        notice.reason
                    } else {
                        "Ran out of materials for " + notice.itemName + ".\\n" + notice.reason
                    }
                )
            },
            confirmButton = {
                androidx.compose.material3.TextButton(onClick = { gameViewModel.dismissActionStoppedNotification() }) {
                    androidx.compose.material3.Text("OK")
                }
            }
        )
    }'''
content = content.replace(anchor_dialog, replacement_dialog, 1)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part M (2/2 - MainActivity.kt) applied cleanly.")

# PART N: Quantity input for the bury stepper - direct numeric entry via a
# text field, plus a "Max" button to select all available bones at once.
path = "app/src/main/kotlin/com/yourname/idlerpg/InventoryScreen.kt"
with open(path, encoding="utf-8") as f:
    content = f.read()

anchor_stepper_row = '''                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(12.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        IconButton(
                            onClick = { if (buryQuantity > 1) buryQuantity -= 1 },
                            enabled = canBuryNow
                        ) {
                            Text(text = "-", style = MaterialTheme.typography.titleLarge)
                        }
                        Text(
                            text = buryQuantity.toString(),
                            style = MaterialTheme.typography.titleMedium,
                            modifier = Modifier.padding(horizontal = 8.dp)
                        )
                        IconButton(
                            onClick = { if (buryQuantity < item.quantity) buryQuantity += 1 },
                            enabled = canBuryNow
                        ) {
                            Text(text = "+", style = MaterialTheme.typography.titleLarge)
                        }
                    }'''
count = content.count(anchor_stepper_row)
assert count == 1, f"Expected 1 match, found {count}."
replacement_stepper_row = '''                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        IconButton(
                            onClick = { if (buryQuantity > 1) buryQuantity -= 1 },
                            enabled = canBuryNow
                        ) {
                            Text(text = "-", style = MaterialTheme.typography.titleLarge)
                        }
                        OutlinedTextField(
                            value = buryQuantity.toString(),
                            onValueChange = { newValue ->
                                val digitsOnly = newValue.filter { it.isDigit() }
                                buryQuantity = when {
                                    digitsOnly.isEmpty() -> 1
                                    else -> (digitsOnly.toIntOrNull() ?: 1).coerceIn(1, item.quantity)
                                }
                            },
                            singleLine = true,
                            enabled = canBuryNow,
                            modifier = Modifier.width(90.dp)
                        )
                        IconButton(
                            onClick = { if (buryQuantity < item.quantity) buryQuantity += 1 },
                            enabled = canBuryNow
                        ) {
                            Text(text = "+", style = MaterialTheme.typography.titleLarge)
                        }
                        TextButton(
                            onClick = { buryQuantity = item.quantity },
                            enabled = canBuryNow
                        ) {
                            Text(text = "Max")
                        }
                    }'''
content = content.replace(anchor_stepper_row, replacement_stepper_row, 1)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Part N (InventoryScreen.kt) applied cleanly.")
