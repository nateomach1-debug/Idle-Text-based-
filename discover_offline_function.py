import subprocess

out = open("discovery_output18.txt", "w", encoding="utf-8")

GVM = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(GVM, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"{'='*80}\nGameViewModel.kt lines 975-1030 (offline resolution function)\n{'='*80}", file=out)
for i in range(974, min(1030, len(lines))):
    print(f"{i+1:5d}: {lines[i]}", end="", file=out)

# find the enclosing function name and its callers
print(f"\n{'='*80}\nSearch for function name enclosing this block\n{'='*80}", file=out)
for i in range(985, 900, -1):
    if "fun " in lines[i]:
        print(f"Function starts at line {i+1}: {lines[i]}", file=out)
        break

out.close()
