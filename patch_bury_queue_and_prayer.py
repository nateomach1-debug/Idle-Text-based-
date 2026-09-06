def apply(content, old, new, label):
    count = content.count(old)
    if count != 1:
        raise SystemExit(f"FAILED [{label}]: expected 1 match, found {count}")
    return content.replace(old, new, 1)

MA_PATH = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
with open(MA_PATH, "r", encoding="utf-8") as f:
    ma = f.read()

ma = apply(ma,
"""    tier = 2,
    guildLevel = 3,
    guildXp = 1200L,
    activeBonusPercent = 5.0,""",
"""    tier = 2,
    guildLevel = 3,
    guildXp = 1200L,
    guildCoins = 500L,
    activeBonusPercent = 5.0,""",
    "demoGuildState: add guildCoins"
)

with open(MA_PATH, "w", encoding="utf-8") as f:
    f.write(ma)

print("Applied successfully.")
