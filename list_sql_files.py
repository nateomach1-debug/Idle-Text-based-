import os

out = open("discovery_output5.txt", "w", encoding="utf-8")
print("SQL files at repo root:", file=out)
for f in sorted(os.listdir(".")):
    if f.endswith(".sql"):
        print(f" - {f}", file=out)
out.close()
