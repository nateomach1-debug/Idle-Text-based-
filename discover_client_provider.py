import re

out = open("discovery_output12.txt", "w", encoding="utf-8")

CP = "app/src/main/kotlin/com/yourname/idlerpg/SupabaseClientProvider.kt"
try:
    with open(CP, "r", encoding="utf-8") as f:
        print(f"{'='*80}\nSupabaseClientProvider.kt (full)\n{'='*80}", file=out)
        print(f.read(), file=out)
except Exception as e:
    print(f"Could not read {CP}: {e}", file=out)

out.close()
