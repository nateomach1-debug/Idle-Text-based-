import kotlin.random.Random

// =========================================================
// ITEM CATEGORY, RARITY, EQUIP SLOTS, ITEM DEFINITION, and
// ITEM CATALOG now all come from SharedTypes.kt -- no longer
// defined here. CombatStyle and EquipmentSlot also come from
// SharedTypes.kt.
// =========================================================

// =========================================================
// RECIPE CATALOG
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
// (ServiceResult now comes from SharedTypes.kt.)
// =========================================================

data class InventorySlotEntry(val itemId: String, var quantity: Int)

class Inventory(
    var maxSlots: Int = 100,
    private val entries: MutableMap<String, InventorySlotEntry> = mutableMapOf(),
    private val equipped: MutableMap<EquipSlot, String> = mutableMapOf()
) {
    fun usedSlots(): Int = entries.size

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
        // Materials are consumed even on failure, per your confirmed design decision.

        return ServiceResult.Success(CraftingResult(succeeded, itemId, if (succeeded) recipe.outputQuantity else 0))
    }
}
