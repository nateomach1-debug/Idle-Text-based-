GVM = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(GVM, "r", encoding="utf-8") as f:
    lines = f.readlines()

out = open("discovery_output20.txt", "w", encoding="utf-8")
for i in range(1029, 1070):
    print(f"{i+1:5d}: {lines[i]}", end="", file=out)
out.close()
