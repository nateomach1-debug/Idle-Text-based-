import re

out = open("discovery_output10.txt", "w", encoding="utf-8")

def search_all_files(pattern, label):
    print(f"\n{'='*80}\n{label}\n{'='*80}", file=out)
    import subprocess
    result = subprocess.run(
        ["grep", "-rn", "--include=*.kt", pattern, "."],
        capture_output=True, text=True
    )
    print(result.stdout if result.stdout else "NO MATCH", file=out)

search_all_files("No local account found", "Grep for the exact error string")
search_all_files("no matching cloud account", "Grep for second half of error string")

out.close()
