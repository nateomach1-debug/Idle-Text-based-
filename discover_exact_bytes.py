GVM = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(GVM, "r", encoding="utf-8") as f:
    content = f.read()

out = open("discovery_output8.txt", "w", encoding="utf-8")

idx = content.find("fun sellItemToVendor")
if idx == -1:
    print("NOT FOUND", file=out)
else:
    # back up to the start of the line (the 4-space indent before 'fun')
    line_start = content.rfind("\n", 0, idx) + 1
    snippet = content[line_start:idx + 700]
    print("--- repr() of exact bytes, function start through ~700 chars ---", file=out)
    print(repr(snippet), file=out)
    print("\n--- same snippet, plain (for visual reference) ---", file=out)
    print(snippet, file=out)

out.close()
