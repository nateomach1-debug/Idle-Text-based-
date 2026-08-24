import re

out = open("discovery_output4.txt", "w", encoding="utf-8")

path = "market_server_sync.sql"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()
lines = content.split("\n")

print(f"File length: {len(lines)} lines\n", file=out)

# 1. Any line containing the exact error message
print("="*80, file=out)
print("Lines matching 'does not belong to caller'", file=out)
print("="*80, file=out)
for i, line in enumerate(lines):
    if "does not belong to caller" in line:
        start = max(0, i - 15)
        end = min(len(lines), i + 5)
        for j in range(start, end):
            print(f"{j+1:5d}: {lines[j]}", file=out)
        print("-"*40, file=out)

# 2. Full market_place_sell_order function definition
print("\n" + "="*80, file=out)
print("Full market_place_sell_order function", file=out)
print("="*80, file=out)
match = re.search(r"create (or replace )?function market_place_sell_order.*?(?=\ncreate (or replace )?function|\Z)",
                   content, re.IGNORECASE | re.DOTALL)
if match:
    print(match.group(0), file=out)
else:
    print("NO MATCH via regex - dumping by line search instead", file=out)
    for i, line in enumerate(lines):
        if "market_place_sell_order" in line.lower() and ("function" in line.lower() or "create" in line.lower()):
            for j in range(i, min(len(lines), i + 80)):
                print(f"{j+1:5d}: {lines[j]}", file=out)
            print("-"*40, file=out)

# 3. Full market_place_buy_order function (for comparison, since buy may or may not share the bug)
print("\n" + "="*80, file=out)
print("Full market_place_buy_order function", file=out)
print("="*80, file=out)
match2 = re.search(r"create (or replace )?function market_place_buy_order.*?(?=\ncreate (or replace )?function|\Z)",
                    content, re.IGNORECASE | re.DOTALL)
if match2:
    print(match2.group(0), file=out)
else:
    print("NO MATCH via regex", file=out)

out.close()
