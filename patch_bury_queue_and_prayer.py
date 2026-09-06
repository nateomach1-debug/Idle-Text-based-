def apply(content, old, new, label):
    count = content.count(old)
    if count != 1:
        raise SystemExit(f"FAILED [{label}]: expected 1 match, found {count}")
    return content.replace(old, new, 1)

# ---------- ItemsEquipmentSystem.kt ----------
IES_PATH = "app/src/main/kotlin/com/yourname/idlerpg/ItemsEquipmentSystem.kt"
with open(IES_PATH, "r", encoding="utf-8") as f:
    ies = f.read()

ies = apply(ies,
"""data class InventorySlotEntry(val itemId: String, val quantity: Int)""",
"""data class InventorySlotEntry(val itemId: String, val quantity: Int, val lastAcquiredAtMillis: Long = System.currentTimeMillis())""",
    "InventorySlotEntry: add lastAcquiredAtMillis"
)

ies = apply(ies,
"""    fun addItem(itemId: String, quantity: Int): ServiceResult<Unit> {
        val definition = ItemCatalog.find(itemId) ?: return ServiceResult.Failure("Unknown item.")
        if (quantity <= 0) return ServiceResult.Failure("Quantity must be positive.")

        val existing = entries[itemId]
        if (existing != null) {
            entries[itemId] = existing.copy(quantity = existing.quantity + quantity)
            return ServiceResult.Success(Unit)
        }

        if (usedSlots() >= maxSlots) return ServiceResult.Failure("Inventory is full.")
        entries[itemId] = InventorySlotEntry(itemId, quantity)
        return ServiceResult.Success(Unit)
    }""",
"""    fun addItem(itemId: String, quantity: Int): ServiceResult<Unit> {
        val definition = ItemCatalog.find(itemId) ?: return ServiceResult.Failure("Unknown item.")
        if (quantity <= 0) return ServiceResult.Failure("Quantity must be positive.")

        val existing = entries[itemId]
        if (existing != null) {
            // Restocking an existing stack counts as "acquired now" too, so
            // "most recent" sorting reflects the last time you got more of
            // something, not just when you first ever picked it up.
            entries[itemId] = existing.copy(quantity = existing.quantity + quantity, lastAcquiredAtMillis = System.currentTimeMillis())
            return ServiceResult.Success(Unit)
        }

        if (usedSlots() >= maxSlots) return ServiceResult.Failure("Inventory is full.")
        entries[itemId] = InventorySlotEntry(itemId, quantity)
        return ServiceResult.Success(Unit)
    }""",
    "addItem: update lastAcquiredAtMillis on restock"
)

ies = apply(ies,
"""    fun allItems(): List<InventorySlotEntry> = entries.values.toList()

    fun restoreItem(itemId: String, quantity: Int) {
        entries[itemId] = InventorySlotEntry(itemId, quantity)
    }""",
"""    fun allItems(): List<InventorySlotEntry> = entries.values.toList()

    fun restoreItem(itemId: String, quantity: Int, lastAcquiredAtMillis: Long = System.currentTimeMillis()) {
        entries[itemId] = InventorySlotEntry(itemId, quantity, lastAcquiredAtMillis)
    }""",
    "restoreItem: accept lastAcquiredAtMillis"
)

ies = apply(ies,
"""data class InventorySlotExport(val characterId: String, val itemId: String, val quantity: Int)""",
"""data class InventorySlotExport(val characterId: String, val itemId: String, val quantity: Int, val lastAcquiredAtMillis: Long = System.currentTimeMillis())""",
    "InventorySlotExport: add lastAcquiredAtMillis"
)

ies = apply(ies,
"""    fun exportAllItems(): List<InventorySlotExport> = inventories.flatMap { (characterId, inv) ->
        inv.allItems().map { InventorySlotExport(characterId, it.itemId, it.quantity) }
    }""",
"""    fun exportAllItems(): List<InventorySlotExport> = inventories.flatMap { (characterId, inv) ->
        inv.allItems().map { InventorySlotExport(characterId, it.itemId, it.quantity, it.lastAcquiredAtMillis) }
    }""",
    "exportAllItems: include lastAcquiredAtMillis"
)

ies = apply(ies,
"""    fun restoreItem(export: InventorySlotExport) {
        inventoryFor(export.characterId).restoreItem(export.itemId, export.quantity)
    }""",
"""    fun restoreItem(export: InventorySlotExport) {
        inventoryFor(export.characterId).restoreItem(export.itemId, export.quantity, export.lastAcquiredAtMillis)
    }""",
    "InventoryService.restoreItem: pass through lastAcquiredAtMillis"
)

with open(IES_PATH, "w", encoding="utf-8") as f:
    f.write(ies)

# ---------- GameStateRepository.kt ----------
GSR_PATH = "app/src/main/kotlin/com/yourname/idlerpg/GameStateRepository.kt"
with open(GSR_PATH, "r", encoding="utf-8") as f:
    gsr = f.read()

gsr = apply(gsr,
"""        val inventoryArray = JSONArray()
        inventoryItems.forEach { entry ->
            val obj = JSONObject()
            obj.put("characterId", entry.characterId)
            obj.put("itemId", entry.itemId)
            obj.put("quantity", entry.quantity)
            inventoryArray.put(obj)
        }
        root.put("inventoryItems", inventoryArray)""",
"""        val inventoryArray = JSONArray()
        inventoryItems.forEach { entry ->
            val obj = JSONObject()
            obj.put("characterId", entry.characterId)
            obj.put("itemId", entry.itemId)
            obj.put("quantity", entry.quantity)
            obj.put("lastAcquiredAtMillis", entry.lastAcquiredAtMillis)
            inventoryArray.put(obj)
        }
        root.put("inventoryItems", inventoryArray)""",
    "write loop: add lastAcquiredAtMillis"
)

gsr = apply(gsr,
"""            inventoryItems.add(
                InventorySlotExport(
                    characterId = obj.getString("characterId"),
                    itemId = obj.getString("itemId"),
                    quantity = obj.getInt("quantity")
                )
            )""",
"""            inventoryItems.add(
                InventorySlotExport(
                    characterId = obj.getString("characterId"),
                    itemId = obj.getString("itemId"),
                    quantity = obj.getInt("quantity"),
                    // optLong with a fallback default so saves written before this
                    // field existed don't crash on load - they just get "now" as a
                    // one-time backfill, which is a harmless, reasonable default.
                    lastAcquiredAtMillis = obj.optLong("lastAcquiredAtMillis", System.currentTimeMillis())
                )
            )""",
    "read loop: backward-compatible lastAcquiredAtMillis read"
)

with open(GSR_PATH, "w", encoding="utf-8") as f:
    f.write(gsr)

# ---------- InventoryScreen.kt ----------
INV_PATH = "app/src/main/kotlin/com/yourname/idlerpg/InventoryScreen.kt"
with open(INV_PATH, "r", encoding="utf-8") as f:
    inv = f.read()

inv = apply(inv,
"""data class InventoryItemSummary(
    val itemId: String,
    val displayName: String,
    val category: InventoryCategory,
    val quantity: Int,
    val isEquippable: Boolean,
    val isConsumable: Boolean,
    val npcValuePerUnit: Long,
    val statsDescription: String? = null, // e.g. "ATK +5, ACC +10" -- only for equippable items
    val isBuryable: Boolean = false
)""",
"""data class InventoryItemSummary(
    val itemId: String,
    val displayName: String,
    val category: InventoryCategory,
    val quantity: Int,
    val isEquippable: Boolean,
    val isConsumable: Boolean,
    val npcValuePerUnit: Long,
    val statsDescription: String? = null, // e.g. "ATK +5, ACC +10" -- only for equippable items
    val isBuryable: Boolean = false,
    val lastAcquiredAtMillis: Long = 0L
)

enum class InventorySortMode(val label: String) {
    RECENT_DESC("Most Recent"),
    RECENT_ASC("Oldest First"),
    ALPHA_ASC("A to Z"),
    ALPHA_DESC("Z to A")
}

private const val KEY_INVENTORY_SORT_MODE = "inventory_sort_mode"

private fun loadSavedInventorySortMode(context: Context): InventorySortMode {
    val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    val saved = prefs.getString(KEY_INVENTORY_SORT_MODE, InventorySortMode.RECENT_DESC.name)
    return runCatching { InventorySortMode.valueOf(saved ?: InventorySortMode.RECENT_DESC.name) }
        .getOrDefault(InventorySortMode.RECENT_DESC)
}

private fun saveInventorySortMode(context: Context, mode: InventorySortMode) {
    val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    prefs.edit().putString(KEY_INVENTORY_SORT_MODE, mode.name).apply()
}

private fun sortedInventoryItems(items: List<InventoryItemSummary>, mode: InventorySortMode): List<InventoryItemSummary> = when (mode) {
    InventorySortMode.RECENT_DESC -> items.sortedByDescending { it.lastAcquiredAtMillis }
    InventorySortMode.RECENT_ASC -> items.sortedBy { it.lastAcquiredAtMillis }
    InventorySortMode.ALPHA_ASC -> items.sortedBy { it.displayName.lowercase() }
    InventorySortMode.ALPHA_DESC -> items.sortedByDescending { it.displayName.lowercase() }
}""",
    "InventoryItemSummary + sort mode enum/helpers"
)

inv = apply(inv,
"""    var viewMode by remember { mutableStateOf(loadSavedInventoryViewMode(context)) }
    var selectedItem by remember { mutableStateOf<InventoryItemSummary?>(null) }

    val grouped = remember(items) {
        InventoryCategory.values().mapNotNull { category ->
            val categoryItems = items.filter { it.category == category }
            if (categoryItems.isEmpty()) null else category to categoryItems
        }
    }""",
"""    var viewMode by remember { mutableStateOf(loadSavedInventoryViewMode(context)) }
    var sortMode by remember { mutableStateOf(loadSavedInventorySortMode(context)) }
    var sortMenuExpanded by remember { mutableStateOf(false) }
    var selectedItem by remember { mutableStateOf<InventoryItemSummary?>(null) }

    val grouped = remember(items, sortMode) {
        InventoryCategory.values().mapNotNull { category ->
            val categoryItems = sortedInventoryItems(items.filter { it.category == category }, sortMode)
            if (categoryItems.isEmpty()) null else category to categoryItems
        }
    }""",
    "add sortMode state + apply sort within each category group"
)

inv = apply(inv,
"""        Spacer(modifier = Modifier.height(8.dp))

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedButton(onClick = onOpenEquipment, modifier = Modifier.weight(1f)) {""",
"""        Spacer(modifier = Modifier.height(8.dp))

        Box {
            TextButton(onClick = { sortMenuExpanded = true }) {
                Text(text = "Sort: " + sortMode.label)
            }
            DropdownMenu(expanded = sortMenuExpanded, onDismissRequest = { sortMenuExpanded = false }) {
                InventorySortMode.values().forEach { option ->
                    DropdownMenuItem(
                        text = { Text(text = option.label) },
                        onClick = {
                            sortMode = option
                            saveInventorySortMode(context, option)
                            sortMenuExpanded = false
                        }
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(8.dp))

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedButton(onClick = onOpenEquipment, modifier = Modifier.weight(1f)) {""",
    "add sort dropdown UI control"
)

with open(INV_PATH, "w", encoding="utf-8") as f:
    f.write(inv)

# ---------- MainActivity.kt ----------
MA_PATH = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
with open(MA_PATH, "r", encoding="utf-8") as f:
    ma = f.read()

ma = apply(ma,
"""            InventoryItemSummary(
                itemId = entry.itemId,
                displayName = definition.name,
                category = mapItemCategory(definition.category),
                quantity = entry.quantity,
                isEquippable = definition.equipSlot != null,
                isConsumable = definition.category == ItemCategory.CONSUMABLE,
                npcValuePerUnit = vendorPayoutFor(entry.itemId),
                statsDescription = statsText,
                isBuryable = PrayerBoneRequirements.containsKey(entry.itemId)
            )""",
"""            InventoryItemSummary(
                itemId = entry.itemId,
                displayName = definition.name,
                category = mapItemCategory(definition.category),
                quantity = entry.quantity,
                isEquippable = definition.equipSlot != null,
                isConsumable = definition.category == ItemCategory.CONSUMABLE,
                npcValuePerUnit = vendorPayoutFor(entry.itemId),
                statsDescription = statsText,
                isBuryable = PrayerBoneRequirements.containsKey(entry.itemId),
                lastAcquiredAtMillis = entry.lastAcquiredAtMillis
            )""",
    "buildInventoryItemSummaries branch 1: pass lastAcquiredAtMillis"
)

ma = apply(ma,
"""            InventoryItemSummary(
                itemId = entry.itemId,
                displayName = entry.itemId.split("_").joinToString(" ") { it.replaceFirstChar { c -> c.uppercase() } },
                category = InventoryCategory.MATERIAL,
                quantity = entry.quantity,
                isEquippable = false,
                isConsumable = false,
                npcValuePerUnit = vendorPayoutFor(entry.itemId)
            )""",
"""            InventoryItemSummary(
                itemId = entry.itemId,
                displayName = entry.itemId.split("_").joinToString(" ") { it.replaceFirstChar { c -> c.uppercase() } },
                category = InventoryCategory.MATERIAL,
                quantity = entry.quantity,
                isEquippable = false,
                isConsumable = false,
                npcValuePerUnit = vendorPayoutFor(entry.itemId),
                lastAcquiredAtMillis = entry.lastAcquiredAtMillis
            )""",
    "buildInventoryItemSummaries branch 2: pass lastAcquiredAtMillis"
)

with open(MA_PATH, "w", encoding="utf-8") as f:
    f.write(ma)

print("All edits applied successfully.")
