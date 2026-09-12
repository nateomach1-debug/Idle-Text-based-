import pathlib

path = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/MarketScreen.kt")
text = path.read_text()

old = """@Composable
private fun PostOrderDialog("""

new = """@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun PostOrderDialog("""

count = text.count(old)
if count == 0:
    raise SystemExit(
        "PATCH FAILED: expected '@Composable\\nprivate fun PostOrderDialog(' not found "
        "in MarketScreen.kt - it may already be patched, or differ from what was expected. "
        "No changes made."
    )
elif count > 1:
    raise SystemExit(
        f"PATCH FAILED: block matched {count} times (expected exactly 1) - "
        "refusing to guess which one. No changes made."
    )

text = text.replace(old, new)
path.write_text(text)
print("Patched MarketScreen.kt: added @OptIn(ExperimentalMaterial3Api::class) to PostOrderDialog.")
