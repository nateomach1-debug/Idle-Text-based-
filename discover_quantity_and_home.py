import subprocess

out = open("discovery_output14.txt", "w", encoding="utf-8")

def grep(pattern, label):
    print(f"\n{'='*80}\n{label}\n{'='*80}", file=out)
    result = subprocess.run(
        ["grep", "-rn", "--include=*.kt", pattern, "."],
        capture_output=True, text=True
    )
    print(result.stdout if result.stdout else "NO MATCH", file=out)

grep("class MarketListingSummary", "class MarketListingSummary definition")
grep("class MarketPriceSummary", "class MarketPriceSummary definition")
grep("fun MarketScreen", "MarketScreen composable definition")
grep("AppDestination.HOME", "MainActivity.kt - Home tab entry")

out.close()
