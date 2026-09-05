def apply(content, old, new, label):
    count = content.count(old)
    if count != 1:
        raise SystemExit(f"FAILED [{label}]: expected 1 match, found {count}")
    return content.replace(old, new, 1)

# ---------- SupabaseGuildRepository.kt ----------
SGR_PATH = "app/src/main/kotlin/com/yourname/idlerpg/SupabaseGuildRepository.kt"
with open(SGR_PATH, "r", encoding="utf-8") as f:
    sgr = f.read()

sgr = apply(sgr,
"""    // TEMPORARY diagnostic field - remove once the missing-event issue is found.
    var lastEventDebug: String = ""

""",
"""""",
    "remove temporary lastEventDebug field"
)

sgr = apply(sgr,
"""            val rawEventRows = client.postgrest.from("guild_events")
                .select { filter { eq("guild_id", guildId) } }
                .decodeList<GuildEventRow>()
            // TEMPORARY diagnostic - remove once the missing-event issue is found.
            // Reuses the existing debug dialog rather than adding new UI.
            lastEventDebug = "guildId=" + guildId +
                " rowCount=" + rawEventRows.size +
                " endsAtValues=" + rawEventRows.map { it.endsAt } +
                " deviceNow=" + Instant.now().toString()
            val activeEvent = rawEventRows
                .filter { Instant.parse(it.endsAt).isAfter(Instant.now()) }""",
"""            val activeEvent = client.postgrest.from("guild_events")
                .select { filter { eq("guild_id", guildId) } }
                .decodeList<GuildEventRow>()
                .filter { Instant.parse(it.endsAt).isAfter(Instant.now()) }""",
    "remove temporary raw-event diagnostic capture"
)

with open(SGR_PATH, "w", encoding="utf-8") as f:
    f.write(sgr)

# ---------- GuildHomeScreen.kt ----------
GHS_PATH = "app/src/main/kotlin/com/yourname/idlerpg/GuildHomeScreen.kt"
with open(GHS_PATH, "r", encoding="utf-8") as f:
    ghs = f.read()

ghs = apply(ghs,
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
    "remove temporary debug text from Guild Action Failed dialog"
)

ghs = apply(ghs,
"""import com.yourname.idlerpg.SupabaseGuildRepository
import androidx.compose.foundation.background""",
"""import androidx.compose.foundation.background""",
    "remove now-unused SupabaseGuildRepository import"
)

with open(GHS_PATH, "w", encoding="utf-8") as f:
    f.write(ghs)

print("Cleanup applied successfully.")
