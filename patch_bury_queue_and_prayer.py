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
"""            val activeEvent = client.postgrest.from("guild_events")
                .select { filter { eq("guild_id", guildId) } }
                .decodeList<GuildEventRow>()
                .filter { Instant.parse(it.endsAt).isAfter(Instant.now()) }
                .maxByOrNull { it.startsAt }
                ?.let {
                    GuildEventSummary(
                        id = it.id,
                        name = it.eventType,
                        itemId = it.itemId ?: "",
                        skillName = it.skillName ?: "",
                        progressCurrent = it.contributedQuantity,
                        progressTarget = it.requiredQuantity ?: 0,
                        milestonesPaid = it.milestonesPaid
                    )
                }""",
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
                .filter { Instant.parse(it.endsAt).isAfter(Instant.now()) }
                .maxByOrNull { it.startsAt }
                ?.let {
                    GuildEventSummary(
                        id = it.id,
                        name = it.eventType,
                        itemId = it.itemId ?: "",
                        skillName = it.skillName ?: "",
                        progressCurrent = it.contributedQuantity,
                        progressTarget = it.requiredQuantity ?: 0,
                        milestonesPaid = it.milestonesPaid
                    )
                }""",
    "fetchGuildHome: add temporary raw-event diagnostic capture"
)

sgr = apply(sgr,
"""object SupabaseGuildRepository {

    private val client get() = SupabaseClientProvider.client""",
"""object SupabaseGuildRepository {

    private val client get() = SupabaseClientProvider.client

    // TEMPORARY diagnostic field - remove once the missing-event issue is found.
    var lastEventDebug: String = """"",
    "add lastEventDebug field"
)

with open(SGR_PATH, "w", encoding="utf-8") as f:
    f.write(sgr)

# ---------- MainActivity.kt ----------
MA_PATH = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
with open(MA_PATH, "r", encoding="utf-8") as f:
    ma = f.read()

ma = apply(ma,
"""                                                debugChatError?.let { androidx.compose.material3.Text("Chat error: $it") }
                                                debugMarketError?.let { androidx.compose.material3.Text("Market error: $it") }
                                            }
                                        },
                                        confirmButton = {""",
"""                                                debugChatError?.let { androidx.compose.material3.Text("Chat error: $it") }
                                                debugMarketError?.let { androidx.compose.material3.Text("Market error: $it") }
                                                androidx.compose.material3.Text("Event debug: " + SupabaseGuildRepository.lastEventDebug)
                                            }
                                        },
                                        confirmButton = {""",
    "MainActivity: show lastEventDebug in existing debug dialog"
)

with open(MA_PATH, "w", encoding="utf-8") as f:
    f.write(ma)

print("Applied successfully.")
