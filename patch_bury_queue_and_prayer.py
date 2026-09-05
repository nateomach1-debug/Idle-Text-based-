def apply(content, old, new, label):
    count = content.count(old)
    if count != 1:
        raise SystemExit(f"FAILED [{label}]: expected 1 match, found {count}")
    return content.replace(old, new, 1)

MA_PATH = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
with open(MA_PATH, "r", encoding="utf-8") as f:
    ma = f.read()

ma = apply(ma,
"""                                                debugChatError?.let { androidx.compose.material3.Text("Chat error: $it") }
                                                debugMarketError?.let { androidx.compose.material3.Text("Market error: $it") }
                                                androidx.compose.material3.Text("Event debug: " + SupabaseGuildRepository.lastEventDebug)
                                            }
                                        },
                                        confirmButton = {""",
"""                                                debugChatError?.let { androidx.compose.material3.Text("Chat error: $it") }
                                                debugMarketError?.let { androidx.compose.material3.Text("Market error: $it") }
                                            }
                                        },
                                        confirmButton = {""",
    "remove now-invalid Event debug line referencing removed lastEventDebug field"
)

with open(MA_PATH, "w", encoding="utf-8") as f:
    f.write(ma)

print("Applied successfully.")
