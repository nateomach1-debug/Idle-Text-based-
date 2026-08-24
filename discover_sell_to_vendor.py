out = open("discovery_output3.txt", "w", encoding="utf-8")

with open("app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "fun sellItemToVendor" in line:
        start = max(0, i - 2)
        end = min(len(lines), i + 40)
        print(f"\n{'='*80}\nGameViewModel.kt - sellItemToVendor full\n{'='*80}", file=out)
        for j in range(start, end):
            print(f"{j+1:5d}: {lines[j]}", end="", file=out)
        break

out.close()
