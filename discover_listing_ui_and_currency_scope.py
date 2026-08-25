out = open("discovery_output15.txt", "w", encoding="utf-8")

MS = "app/src/main/kotlin/com/yourname/idlerpg/MarketScreen.kt"
MA = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"

with open(MS, "r", encoding="utf-8") as f:
    ms_lines = f.readlines()

print(f"{'='*80}\nMarketScreen.kt lines 1-90 (data classes + start of composable)\n{'='*80}", file=out)
for i in range(0, min(90, len(ms_lines))):
    print(f"{i+1:5d}: {ms_lines[i]}", end="", file=out)

# find where "For Sale" / listing rows are rendered (search for bestSellPrice usage in UI)
print(f"\n{'='*80}\nMarketScreen.kt - listing row rendering (bestSellPrice usage)\n{'='*80}", file=out)
for i, line in enumerate(ms_lines):
    if "bestSellPrice" in line or "bestBuyPrice" in line:
        start = max(0, i - 3)
        end = min(len(ms_lines), i + 10)
        for j in range(start, end):
            print(f"{j+1:5d}: {ms_lines[j]}", end="", file=out)
        print("-"*40, file=out)

with open(MA, "r", encoding="utf-8") as f:
    ma_lines = f.readlines()

print(f"\n{'='*80}\nMainActivity.kt lines 450-470 (currency collection context)\n{'='*80}", file=out)
for i in range(449, min(470, len(ma_lines))):
    print(f"{i+1:5d}: {ma_lines[i]}", end="", file=out)

print(f"\n{'='*80}\nMainActivity.kt lines 625-645 (HOME block context)\n{'='*80}", file=out)
for i in range(624, min(645, len(ma_lines))):
    print(f"{i+1:5d}: {ma_lines[i]}", end="", file=out)

out.close()
