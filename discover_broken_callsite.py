EMS = "app/src/main/kotlin/com/yourname/idlerpg/EconomyMarketSystem.kt"
with open(EMS, "r", encoding="utf-8") as f:
    lines = f.readlines()

out = open("discovery_output16.txt", "w", encoding="utf-8")
start = max(0, 323 - 10)
end = min(len(lines), 323 + 5)
for i in range(start, end):
    print(f"{i+1:5d}: {lines[i]}", end="", file=out)
out.close()
