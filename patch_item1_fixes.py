import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"

def find_file(name):
    for dirpath, _, files in os.walk(ROOT):
        if name in files:
            return os.path.join(dirpath, name)
    raise SystemExit(f"!!! FILE NOT FOUND: {name} !!!")

def guarded_replace(path, old, new, expected_count=1):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    count = content.count(old)
    if count != expected_count:
        raise SystemExit(
            f"!!! ABORTING: expected {expected_count} occurrence(s) of anchor in {path}, found {count} !!!\n"
            f"--- anchor was ---\n{old}\n--- end anchor ---"
        )
    content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"patched {path} (replaced {count} occurrence(s))")

# ---------------------------------------------------------------------------
# 1. GeneratedItemCatalog.kt - add the 5 missing item definitions + values
# ---------------------------------------------------------------------------
catalog_path = find_file("GeneratedItemCatalog.kt")

definitions_old = """    ItemDefinition(
        id = "monarchs_purse",
        name = "Monarch's Purse",
        category = ItemCategory.MATERIAL,
        isTradeable = true,
        isStackable = true
    ),
    )
"""
definitions_new = """    ItemDefinition(
        id = "monarchs_purse",
        name = "Monarch's Purse",
        category = ItemCategory.MATERIAL,
        isTradeable = true,
        isStackable = true
    ),
    ItemDefinition(
        id = "bone",
        name = "Bone",
        category = ItemCategory.MATERIAL,
        isTradeable = true,
        isStackable = true
    ),
    ItemDefinition(
        id = "goblin_ear",
        name = "Goblin Ear",
        category = ItemCategory.MATERIAL,
        isTradeable = true,
        isStackable = true
    ),
    ItemDefinition(
        id = "rusty_dagger",
        name = "Rusty Dagger",
        category = ItemCategory.MATERIAL,
        isTradeable = true,
        isStackable = true
    ),
    ItemDefinition(
        id = "ectoplasm",
        name = "Ectoplasm",
        category = ItemCategory.MATERIAL,
        isTradeable = true,
        isStackable = true
    ),
    ItemDefinition(
        id = "wraith_essence",
        name = "Wraith Essence",
        category = ItemCategory.MATERIAL,
        isTradeable = true,
        isStackable = true
    ),
    )
"""
guarded_replace(catalog_path, definitions_old, definitions_new)

values_old = """    "monarchs_purse" to 3000L,
    )
"""
values_new = """    "monarchs_purse" to 3000L,
    "bone" to 2L,
    "goblin_ear" to 1L,
    "rusty_dagger" to 12L,
    "ectoplasm" to 8L,
    "wraith_essence" to 30L,
    )
"""
guarded_replace(catalog_path, values_old, values_new)

# ---------------------------------------------------------------------------
# 2. MarketScreen.kt - empty-state text for SellToVendorTab / BuyFromVendorTab
# ---------------------------------------------------------------------------
market_screen_path = find_file("MarketScreen.kt")

sell_tab_old = """private fun SellToVendorTab(items: List<InventoryItemSummary>, onSell: (String, Int) -> Unit) {
    LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        items(items) { item ->
            VendorItemRow(item, onSell)
        }
    }
}"""
sell_tab_new = """private fun SellToVendorTab(items: List<InventoryItemSummary>, onSell: (String, Int) -> Unit) {
    LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        if (items.isEmpty()) {
            item { Text(text = "You have nothing sellable right now.", style = MaterialTheme.typography.bodyMedium) }
        }
        items(items) { item ->
            VendorItemRow(item, onSell)
        }
    }
}"""
guarded_replace(market_screen_path, sell_tab_old, sell_tab_new)

buy_tab_old = """private fun BuyFromVendorTab(items: List<VendorBuyableItem>, onBuy: (String, Int) -> Unit) {
    LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        items(items) { item ->
            VendorBuyItemRow(item, onBuy)
        }
    }
}"""
buy_tab_new = """private fun BuyFromVendorTab(items: List<VendorBuyableItem>, onBuy: (String, Int) -> Unit) {
    LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        if (items.isEmpty()) {
            item { Text(text = "The vendor has nothing for sale right now.", style = MaterialTheme.typography.bodyMedium) }
        }
        items(items) { item ->
            VendorBuyItemRow(item, onBuy)
        }
    }
}"""
guarded_replace(market_screen_path, buy_tab_old, buy_tab_new)

print("ALL PATCHES APPLIED SUCCESSFULLY")
