def apply(content, old, new, label):
    count = content.count(old)
    if count != 1:
        raise SystemExit(f"FAILED [{label}]: expected 1 match, found {count}")
    return content.replace(old, new, 1)

GHS_PATH = "app/src/main/kotlin/com/yourname/idlerpg/GuildHomeScreen.kt"
with open(GHS_PATH, "r", encoding="utf-8") as f:
    ghs = f.read()

ghs = apply(ghs,
"""    actionError?.let { error ->
        AlertDialog(
            onDismissRequest = onDismissError,
            title = { Text(text = "Guild Action Failed") },
            text = { Text(text = error) },
            confirmButton = {
                TextButton(onClick = onDismissError) { Text(text = "OK") }
            }
        )
    }""",
"""    actionError?.let { error ->
        AlertDialog(
            onDismissRequest = onDismissError,
            title = { Text(text = "Guild Action Failed") },
            text = {
                Column {
                    Text(text = error)
                    Spacer(modifier = Modifier.height(8.dp))
                    // TEMPORARY diagnostic - remove once the missing-event issue is found.
                    Text(text = "Event debug: " + SupabaseGuildRepository.lastEventDebug, style = MaterialTheme.typography.labelSmall)
                }
            },
            confirmButton = {
                TextButton(onClick = onDismissError) { Text(text = "OK") }
            }
        )
    }""",
    "GuildHomeScreen: surface lastEventDebug in the dialog that actually shows"
)

with open(GHS_PATH, "w", encoding="utf-8") as f:
    f.write(ghs)

print("Applied successfully.")
