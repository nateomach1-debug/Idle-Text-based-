import kotlin.random.Random

// =========================================================
// ITEM CATEGORY & RARITY
// =========================================================

enum class ItemCategory { WEAPON, ARMOR, ACCESSORY, MATERIAL, CONSUMABLE }

enum class Rarity { COMMON, UNCOMMON, RARE, EPIC, LEGENDARY }

enum class EquipSlot { WEAPON, HELMET, CHESTPLATE, GLOVES, BOOTS, NECKLACE, RING_1, RING_2 }

/** Maps each specific equip slot to the broader lock category Combat System already uses. */
object SlotLockMapping {
    fun lockCategoryFor(slot: EquipSlot): EquipmentSlot = when (slot) {
        EquipSlot.WEAPON -> EquipmentSlot.WEAPON
        EquipSlot.HELMET, EquipSlot.CHESTPLATE, EquipSlot.GLOVES, EquipSlot.BOOTS -> EquipmentSlot.ARMOR
        EquipSlot.NECKLACE, EquipSlot.RING_1, EquipSlot.RING_2 -> EquipmentSlot.ACCESSORY
    }
}

// Reused from Combat System -- same three lock categories, recovery only ever locks WEAPON.
enum class EquipmentSlot { WEAPON, ARMOR, ACCESSORY }

// =========================================================
// ITEM DEFINITION
// (Same name + rarity = always identical stats. No per-instance
//  variance -- "Rare Iron Sword" is its own fixed definition,
//  distinct from "Common Iron Sword," not a random roll on one item.)
// =========================================================

data class ItemStats(
    val attackBonus: Int = 0,
    val strengthBonus: Int = 0,
    val defenseBonus: Int = 0,
    val accuracyBonus: Int = 0,
    val maxHitBonus: Int = 0
)

data class ItemDefinition(
    val id: String, // unique per name+rarity combination, e.g. "iron_sword_rare"
    val name: String,
    val category: ItemCategory,
    val rarity: Rarity,
    val isTradeable: Boolean,
    val isStackable: Boolean, // materials/consumables = true, weapon/armor/accessory = false
    val equipSlot: EquipSlot? = null, // null unless category is WEAPON, ARMOR, or ACCESSORY
    val combatStyle: CombatStyle? = null, // required if category == WEAPON, exactly one style
    val levelRequired: Int = 1,
    val skillRequired: String? = null, // e.g. "ATTACK" -- null if no skill gate
    val stats: ItemStats = ItemStats()
)

// Reused from Combat System.
enum class CombatStyle { MELEE, RANGED, MAGIC }

object ItemCatalog {
    val items = listOf(
        ItemDefinition(
            id = "iron_sword_common",
            name = "Iron Sword",
            category = ItemCategory.WEAPON,
            rarity = Rarity.COMMON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            levelRequired = 10,
            skillRequired = "ATTACK",
            stats = ItemStats(attackBonus = 5, accuracyBonus = 10, maxHitBonus = 6)
        ),
        ItemDefinition(
            id = "iron_sword_rare",
            name = "Iron Sword",
            category = ItemCategory.WEAPON,
            rarity = Rarity.RARE,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            levelRequired = 10,
            skillRequired = "ATTACK",
            stats = ItemStats(attackBonus = 9, accuracyBonus = 16, maxHitBonus = 10) // same name, higher rarity, better fixed stats
        ),
        ItemDefinition(
            id = "leather_boots_common",
            name = "Leather Boots",
            category = ItemCategory.ARMOR,
            rarity = Rarity.COMMON,
            isTradeable = true,
            isStackable = false,
            equipSlot = EquipSlot.BOOTS,
            levelRequired = 1,
            stats = ItemStats(defenseBonus = 3)
        ),
        ItemDefinition(
            id = "iron_ore",
            name = "Iron Ore",
            category = ItemCategory.MATERIAL,
            rarity = Rarity.COMMON,
            isTradeable = true,
            isStackable = true
        ),
        ItemDefinition(
            id = "steel_bar",
            name = "Steel Bar",
            category = ItemCategory.MATERIAL,
            rarity = Rarity.COMMON,
            isTradeable = true,
            isStackable = true
        ),
        ItemDefinition(
            id = "minor_healing_potion",
            name = "Minor Healing Potion",
            category = ItemCategory.CONSUMABLE,
            rarity = Rarity.COMMON,
            isTradeable = true,
            isStackable = true
        ),
        ItemDefinition(
            id = "smiths_hammer",
            name = "Smith's Hammer",
            category = ItemCategory.WEAPON,
            rarity = Rarity.UNCOMMON,
            isTradeable = false, // quest reward, per Quests module
            isStackable = false,
            equipSlot = EquipSlot.WEAPON,
            combatStyle = CombatStyle.MELEE,
            levelRequired = 1,
            stats = ItemStats(attackBonus = 2, maxHitBonus = 2)
        )
    )

    fun find(itemId: String): ItemDefinition? = items.find { it.id == itemId }
    fun findByNameAndRarity(name: String, rarity: Rarity): ItemDefinition? =
        items.find { it.name == name && it.rarity == rarity }
}

// =========================================================
// RECIPE CATALOG (referenced by the Offline crafting queue)
// =========================================================

data class RecipeIngredient(val itemId: String, val quantity: Int)

data class Recipe(
    val outputItemId: String,
    val outputQuantity: Int,
    val ingredients: List<RecipeIngredient>,
    val skillRequired: String,
    val levelRequired: Int
)

object RecipeCatalog {
    val recipes = listOf(
        Recipe(
            outputItemId = "steel_bar",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("iron_ore", 2)),
            skillRequired = "SMITHING",
            levelRequired = 20
        ),
        Recipe(
            outputItemId = "iron_sword_common",
            outputQuantity = 1,
            ingredients = listOf(RecipeIngredient("steel_bar", 3)),
            skillRequired = "SMITHING",
            levelRequired = 30
        )
    )

    fun forOutput(itemId: String): Recipe? = recipes.find { it.outputItemId == itemId }
}

// =========================================================
// CRAFTING SUCCESS CALCULATION
// =========================================================

object CraftingSuccessCalculator {
    private const val BASE_SUCCESS_PERCENT = 80.0
    private const val PERCENT_PER_LEVEL_ABOVE = 1.0

    fun successChancePercent(playerSkillLevel: Int, recipe: Recipe): Double {
        val levelsAbove = (playerSkillLevel - recipe.levelRequired).coerceAtLeast(0)
        val chance = BASE_SUCCESS_PERCENT + (levelsAbove * PERCENT_PER_LEVEL_ABOVE)
        return chance.coerceAtMost(100.0)
    }

    fun rollSuccess(playerSkillLevel: Int, recipe: Recipe): Boolean {
        val chance = successChancePercent(playerSkillLevel, recipe)
        return Random.nextDouble(0.0, 100.0) < chance
    }
}

// =========================================================
// INVENTORY
// =========================================================

data class InventorySlotEntry(val itemId: String, var quantity: Int) // quantity > 1 only valid if stackable

class Inventory(
    var maxSlots: Int = 100,
    private val entries: MutableMap<String, InventorySlotEntry> = mutableMapOf(), // itemId -> entry, one entry per item
    private val equipped: MutableMap<EquipSlot, String> = mutableMapOf() // slot -> itemId
) {
    fun usedSlots(): Int = entries.size // each distinct item = 1 slot, regardless of stack quantity

    fun addItem(itemId: String, quantity: Int): ServiceResult<Unit> {
        val definition = ItemCatalog.find(itemId) ?: return ServiceResult.Failure("Unknown item.")
        if (quantity <= 0) return ServiceResult.Failure("Quantity must be positive.")

        val existing = entries[itemId]
        if (existing != null) {
            if (!definition.isStackable) return ServiceResult.Failure("Item is not stackable and already present.")
            existing.quantity += quantity
            return ServiceResult.Success(Unit)
        }

        if (usedSlots() >= maxSlots) return ServiceResult.Failure("Inventory is full.")
        entries[itemId] = InventorySlotEntry(itemId, quantity)
        return ServiceResult.Success(Unit)
    }

    fun removeItem(itemId: String, quantity: Int): ServiceResult<Unit> {
        val entry = entries[itemId] ?: return ServiceResult.Failure("Item not in inventory.")
        if (entry.quantity < quantity) return ServiceResult.Failure("Not enough quantity to remove.")

        entry.quantity -= quantity
        if (entry.quantity <= 0) entries.remove(itemId)
        return ServiceResult.Success(Unit)
    }

    fun quantityOf(itemId: String): Int = entries[itemId]?.quantity ?: 0

    fun expandCapacity(additionalSlots: Int) {
        maxSlots += additionalSlots
    }

    // ---------------- Equipping ----------------

    fun equippedItemIn(slot: EquipSlot): String? = equipped[slot]

    fun equip(itemId: String, playerLevel: Int, playerSkillLevels: Map<String, Int>, canChangeSlot: (EquipmentSlot) -> Boolean): ServiceResult<Unit> {
        val definition = ItemCatalog.find(itemId) ?: return ServiceResult.Failure("Unknown item.")
        val slot = definition.equipSlot ?: return ServiceResult.Failure("This item cannot be equipped.")

        val lockCategory = SlotLockMapping.lockCategoryFor(slot)
        if (!canChangeSlot(lockCategory)) {
            return ServiceResult.Failure("Cannot change " + lockCategory.name + " slot right now.")
        }
        if (quantityOf(itemId) <= 0) return ServiceResult.Failure("Item not in inventory.")
        if (playerLevel < definition.levelRequired) {
            return ServiceResult.Failure("Requires level " + definition.levelRequired + ".")
        }
        definition.skillRequired?.let { skillId ->
            val playerSkillLevel = playerSkillLevels[skillId] ?: 0
            if (playerSkillLevel < definition.levelRequired) {
                return ServiceResult.Failure("Requires " + skillId + " level " + definition.levelRequired + ".")
            }
        }

        // Unequip whatever was already there, back into inventory.
        equipped[slot]?.let { previousItemId ->
            addItem(previousItemId, 1)
        }

        removeItem(itemId, 1)
        equipped[slot] = itemId
        return ServiceResult.Success(Unit)
    }

    fun unequip(slot: EquipSlot, canChangeSlot: (EquipmentSlot) -> Boolean): ServiceResult<Unit> {
        val lockCategory = SlotLockMapping.lockCategoryFor(slot)
        if (!canChangeSlot(lockCategory)) {
            return ServiceResult.Failure("Cannot change " + lockCategory.name + " slot right now.")
        }
        val itemId = equipped[slot] ?: return ServiceResult.Failure("Nothing equipped in that slot.")

        addItem(itemId, 1)
        equipped.remove(slot)
        return ServiceResult.Success(Unit)
    }

    fun allEquipped(): Map<EquipSlot, String> = equipped.toMap()
}

// =========================================================
// RESULT TYPE
// =========================================================

sealed class ServiceResult<out T> {
    data class Success<T>(val value: T) : ServiceResult<T>()
    data class Failure(val reason: String) : ServiceResult<Nothing>()
}

// =========================================================
// CRAFTING SERVICE
// =========================================================

class CraftingResult(val succeeded: Boolean, val itemId: String, val quantityProduced: Int)

class CraftingService {
    fun craftOnce(inventory: Inventory, itemId: String, playerSkillLevel: Int): ServiceResult<CraftingResult> {
        val recipe = RecipeCatalog.forOutput(itemId) ?: return ServiceResult.Failure("No recipe for this item.")
        if (playerSkillLevel < recipe.levelRequired) {
            return ServiceResult.Failure("Requires " + recipe.skillRequired + " level " + recipe.levelRequired + ".")
        }

        for (ingredient in recipe.ingredients) {
            if (inventory.quantityOf(ingredient.itemId) < ingredient.quantity) {
                return ServiceResult.Failure("Missing materials: " + ingredient.itemId)
            }
        }

        for (ingredient in recipe.ingredients) {
            inventory.removeItem(ingredient.itemId, ingredient.quantity)
        }

        val succeeded = CraftingSuccessCalculator.rollSuccess(playerSkillLevel, recipe)
        if (succeeded) {
            inventory.addItem(recipe.outputItemId, recipe.outputQuantity)
        }
        // On failure, materials are still consumed -- this is a real design implication
        // worth flagging: chance-based crafting means failed attempts cost materials.

        return ServiceResult.Success(CraftingResult(succeeded, itemId, if (succeeded) recipe.outputQuantity else 0))
    }
}

// =========================================================
// DEMO
// =========================================================

fun main() {
    val inventory = Inventory()

    println("=== Adding starting materials ===")
    printResult(inventory.addItem("iron_ore", 10))
    printResult(inventory.addItem("iron_sword_common", 1))
    printResult(inventory.addItem("leather_boots_common", 1))

    println("")
    println("=== Checking used slots (each distinct item = 1 slot, regardless of stack size) ===")
    println("Used slots: " + inventory.usedSlots() + " / " + inventory.maxSlots)

    println("")
    println("=== Equipping the Iron Sword (no lock restrictions right now) ===")
    val alwaysAllowed: (EquipmentSlot) -> Boolean = { true }
    printResult(inventory.equip("iron_sword_common", playerLevel = 15, playerSkillLevels = mapOf("ATTACK" to 15), canChangeSlot = alwaysAllowed))
    println("Equipped weapon: " + inventory.equippedItemIn(EquipSlot.WEAPON))

    println("")
    println("=== Attempting to equip while the WEAPON slot is locked (simulating recovery) ===")
    val weaponLocked: (EquipmentSlot) -> Boolean = { it != EquipmentSlot.WEAPON }
    printResult(inventory.equip("smiths_hammer", playerLevel = 15, playerSkillLevels = mapOf("ATTACK" to 15), canChangeSlot = weaponLocked))

    println("")
    println("=== Equipping boots while WEAPON is locked (should succeed -- ARMOR is unaffected by recovery lock) ===")
    printResult(inventory.equip("leather_boots_common", playerLevel = 1, playerSkillLevels = emptyMap(), canChangeSlot = weaponLocked))

    println("")
    println("=== Attempting to equip an item without meeting the skill requirement ===")
    inventory.addItem("iron_sword_rare", 1)
    printResult(inventory.equip("iron_sword_rare", playerLevel = 5, playerSkillLevels = mapOf("ATTACK" to 5), canChangeSlot = alwaysAllowed))

    println("")
    println("=== Confirming Common and Rare Iron Sword have different fixed stats (same name, different rarity) ===")
    val common = ItemCatalog.findByNameAndRarity("Iron Sword", Rarity.COMMON)
    val rare = ItemCatalog.findByNameAndRarity("Iron Sword", Rarity.RARE)
    println("Common: " + common?.stats)
    println("Rare: " + rare?.stats)

    println("")
    println("=== Crafting: gathering enough Iron Ore for a Steel Bar recipe ===")
    inventory.addItem("iron_ore", 2) // total now 12, recipe needs 2
    val crafting = CraftingService()
    val craftResult = crafting.craftOnce(inventory, "steel_bar", playerSkillLevel = 25)
    printResult(craftResult)
    if (craftResult is ServiceResult.Success) {
        println("Success chance was: " + CraftingSuccessCalculator.successChancePercent(25, RecipeCatalog.forOutput("steel_bar")!!) + "%")
        println("Steel bars in inventory: " + inventory.quantityOf("steel_bar"))
        println("Iron ore remaining: " + inventory.quantityOf("iron_ore"))
    }

    println("")
    println("=== Crafting below the level requirement (should fail outright) ===")
    printResult(crafting.craftOnce(inventory, "steel_bar", playerSkillLevel = 10))

    println("")
    println("=== Expanding inventory capacity (simulating a paid unlock) ===")
    println("Before: " + inventory.maxSlots)
    inventory.expandCapacity(20)
    println("After: " + inventory.maxSlots)
}

fun <T> printResult(result: ServiceResult<T>) {
    when (result) {
        is ServiceResult.Success -> println("[OK] " + result.value)
        is ServiceResult.Failure -> println("[FAIL] " + result.reason)
    }
}
