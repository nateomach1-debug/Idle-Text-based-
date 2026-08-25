GVM = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(GVM, "r", encoding="utf-8") as f:
    lines = f.readlines()

out = open("discovery_output11.txt", "w", encoding="utf-8")

# find the line with the error message, then walk backward to the enclosing 'fun'
target = None
for i, line in enumerate(lines):
    if "No local account found, and no matching cloud account either" in line:
        target = i
        break

if target is None:
    print("NOT FOUND", file=out)
else:
    # walk backward to find the start of the function
    fn_start = target
    while fn_start > 0 and "fun " not in lines[fn_start]:
        fn_start -= 1
    start = max(0, fn_start - 2)
    end = min(len(lines), target + 15)
    for j in range(start, end):
        print(f"{j+1:5d}: {lines[j]}", end="", file=out)

out.close()
