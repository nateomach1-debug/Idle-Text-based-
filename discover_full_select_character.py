GVM = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(GVM, "r", encoding="utf-8") as f:
    lines = f.readlines()

out = open("discovery_output19.txt", "w", encoding="utf-8")
for i in range(937, 1035):
    print(f"{i+1:5d}: {lines[i]}", end="", file=out)
out.close()
