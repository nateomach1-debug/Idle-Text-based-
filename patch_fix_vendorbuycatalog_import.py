GAME_VIEW_MODEL = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"


def main():
    with open(GAME_VIEW_MODEL, "r", encoding="utf-8") as fh:
        content = fh.read()

    before = content.count("{") - content.count("}")

    old = '''import com.yourname.idlerpg.ui.components.DmConversationSummary

data class OfflineSummary('''
    assert content.count(old) == 1, f"expected 1 occurrence, found {content.count(old)}"

    new = '''import com.yourname.idlerpg.ui.components.DmConversationSummary
import com.yourname.idlerpg.ui.screens.VendorBuyCatalog

data class OfflineSummary('''

    content = content.replace(old, new)

    after = content.count("{") - content.count("}")
    assert before == after, f"brace balance changed: {before} -> {after}"

    with open(GAME_VIEW_MODEL, "w", encoding="utf-8") as fh:
        fh.write(content)
    print(f"Patched {GAME_VIEW_MODEL} (brace balance unchanged: {before})")


if __name__ == "__main__":
    main()
