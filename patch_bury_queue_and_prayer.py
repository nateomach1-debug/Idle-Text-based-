def apply(content, old, new, label):
    count = content.count(old)
    if count != 1:
        raise SystemExit(f"FAILED [{label}]: expected 1 match, found {count}")
    return content.replace(old, new, 1)

GHS_PATH = "app/src/main/kotlin/com/yourname/idlerpg/GuildHomeScreen.kt"
with open(GHS_PATH, "r", encoding="utf-8") as f:
    ghs = f.read()

ghs = apply(ghs,
"""package com.yourname.idlerpg.ui.screens

import androidx.compose.foundation.background""",
"""package com.yourname.idlerpg.ui.screens

import com.yourname.idlerpg.SupabaseGuildRepository
import androidx.compose.foundation.background""",
    "add missing SupabaseGuildRepository import"
)

with open(GHS_PATH, "w", encoding="utf-8") as f:
    f.write(ghs)

print("Applied successfully.")
