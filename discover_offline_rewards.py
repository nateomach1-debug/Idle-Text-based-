import subprocess

out = open("discovery_output17.txt", "w", encoding="utf-8")

def grep(pattern, label):
    print(f"\n{'='*80}\n{label}\n{'='*80}", file=out)
    result = subprocess.run(
        ["grep", "-rn", "--include=*.kt", "-i", pattern, "."],
        capture_output=True, text=True
    )
    print(result.stdout if result.stdout else "NO MATCH", file=out)

grep("offline", "Grep for 'offline' (case-insensitive) across all kt files")

out.close()
