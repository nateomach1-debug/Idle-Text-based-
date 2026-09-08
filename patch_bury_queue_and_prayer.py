#!/usr/bin/env python3
"""
Guarded patch: Skill mastery perks (level 50) + skill capes (level 99).

Touches: SkillProgressionSystem.kt (new Effect types, EffectStacker sums,
16 UnlockTable entries), GameViewModel.kt (cape bonus effects, combat/
gathering/crafting mastery hooks, vendor level-gating), ItemsEquipmentSystem.kt
(craftOnce material-save + success-bonus params), SharedTypes.kt (16 cape
ItemDefinitions), MarketScreen.kt (16 cape VendorBuyableItem entries),
MainActivity.kt (effect display branches + vendor call site).

Run from repo root, same convention as prior patches this project.
"""
import os

ROOT = "app/src/main/kotlin/com/yourname/idlerpg"


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def guarded_replace(path, old, new, already_applied_marker=None):
    content = read(path)
    if already_applied_marker and already_applied_marker in content:
        print(f"SKIP (already applied): {path} :: {already_applied_marker[:50]}")
        return
    count = content.count(old)
    if count != 1:
        raise RuntimeError(
            f"Expected exactly 1 match in {path}, found {count}.\n"
            f"--- old_str ---\n{old}\n--- end ---"
        )
    write(path, content.replace(old, new))
    print(f"PATCHED: {path} :: {already_applied_marker[:50] if already_applied_marker else old[:50]}")


# =======================================================================
# 1. SkillProgressionSystem.kt - new Effect types
# =======================================================================
sps_path = os.path.join(ROOT, "SkillProgressionSystem.kt")

guarded_replace(
    sps_path,
    old='    data class TimerReduction(val scope: EffectScope, val percent: Double) : Effect()\n}',
    new=(
        '    data class TimerReduction(val scope: EffectScope, val percent: Double) : Effect()\n'
        '    data class MaterialSaveChance(val scope: EffectScope, val percent: Double) : Effect()\n'
        '    data class CraftSuccessBoost(val scope: EffectScope, val percent: Double) : Effect()\n'
        '}'
    ),
    already_applied_marker="data class MaterialSaveChance(val scope: EffectScope",
)

# 1b. EffectStacker sums for the two new types
guarded_replace(
    sps_path,
    old=(
        '    fun totalTimerReductionPercent(effects: List<Effect>, skill: SkillType): Double =\n'
        '        effects.filterIsInstance<Effect.TimerReduction>().filter { appliesTo(it.scope, skill) }.sumOf { it.percent }\n'
    ),
    new=(
        '    fun totalTimerReductionPercent(effects: List<Effect>, skill: SkillType): Double =\n'
        '        effects.filterIsInstance<Effect.TimerReduction>().filter { appliesTo(it.scope, skill) }.sumOf { it.percent }\n'
        '\n'
        '    fun totalMaterialSaveChancePercent(effects: List<Effect>, skill: SkillType): Double =\n'
        '        effects.filterIsInstance<Effect.MaterialSaveChance>().filter { appliesTo(it.scope, skill) }.sumOf { it.percent }\n'
        '\n'
        '    fun totalCraftSuccessBoostPercent(effects: List<Effect>, skill: SkillType): Double =\n'
        '        effects.filterIsInstance<Effect.CraftSuccessBoost>().filter { appliesTo(it.scope, skill) }.sumOf { it.percent }\n'
    ),
    already_applied_marker="fun totalMaterialSaveChancePercent",
)

# 1c. UnlockTable - 16 new level-50 mastery entries
guarded_replace(
    sps_path,
    old=(
        '        SkillUnlock(SkillType.MAGIC, 40, listOf(\n'
        '            Effect.TimerReduction(EffectScope.Group(SkillGroup.PRODUCTION), 5.0),\n'
        '            Effect.AccessUnlock("Teleportation spell")\n'
        '        ))\n'
        '    )'
    ),
    new=(
        '        SkillUnlock(SkillType.MAGIC, 40, listOf(\n'
        '            Effect.TimerReduction(EffectScope.Group(SkillGroup.PRODUCTION), 5.0),\n'
        '            Effect.AccessUnlock("Teleportation spell")\n'
        '        )),\n'
        '        // ---- Mastery perks (level 50, one per skill) ----\n'
        '        SkillUnlock(SkillType.ATTACK, 50, listOf(\n'
        '            Effect.AccessUnlock("Combat Mastery: +5% hit chance (melee)"),\n'
        '            Effect.XpBoost(EffectScope.SingleSkill(SkillType.ATTACK), 5.0)\n'
        '        )),\n'
        '        SkillUnlock(SkillType.STRENGTH, 50, listOf(\n'
        '            Effect.AccessUnlock("Combat Mastery: +5% min/max hit damage (melee)"),\n'
        '            Effect.XpBoost(EffectScope.SingleSkill(SkillType.STRENGTH), 5.0)\n'
        '        )),\n'
        '        SkillUnlock(SkillType.DEFENSE, 50, listOf(\n'
        '            Effect.AccessUnlock("Combat Mastery: +5% incoming damage reduction"),\n'
        '            Effect.XpBoost(EffectScope.SingleSkill(SkillType.DEFENSE), 5.0)\n'
        '        )),\n'
        '        SkillUnlock(SkillType.ARCHERY, 50, listOf(\n'
        '            Effect.AccessUnlock("Combat Mastery: +5% hit chance (ranged)"),\n'
        '            Effect.XpBoost(EffectScope.SingleSkill(SkillType.ARCHERY), 5.0)\n'
        '        )),\n'
        '        SkillUnlock(SkillType.MAGIC, 50, listOf(\n'
        '            Effect.AccessUnlock("Combat Mastery: +5% hit chance (magic)"),\n'
        '            Effect.XpBoost(EffectScope.SingleSkill(SkillType.MAGIC), 5.0)\n'
        '        )),\n'
        '        SkillUnlock(SkillType.PRAYER, 50, listOf(\n'
        '            Effect.AccessUnlock("Combat Mastery: +5% reduced monster damage while a prayer is active"),\n'
        '            Effect.XpBoost(EffectScope.SingleSkill(SkillType.PRAYER), 5.0)\n'
        '        )),\n'
        '        SkillUnlock(SkillType.MINING, 50, listOf(\n'
        '            Effect.DropRateBoost(EffectScope.SingleSkill(SkillType.MINING), 10.0),\n'
        '            Effect.XpBoost(EffectScope.SingleSkill(SkillType.MINING), 5.0)\n'
        '        )),\n'
        '        SkillUnlock(SkillType.WOODCUTTING, 50, listOf(\n'
        '            Effect.DropRateBoost(EffectScope.SingleSkill(SkillType.WOODCUTTING), 10.0),\n'
        '            Effect.XpBoost(EffectScope.SingleSkill(SkillType.WOODCUTTING), 5.0)\n'
        '        )),\n'
        '        SkillUnlock(SkillType.FISHING, 50, listOf(\n'
        '            Effect.DropRateBoost(EffectScope.SingleSkill(SkillType.FISHING), 10.0),\n'
        '            Effect.XpBoost(EffectScope.SingleSkill(SkillType.FISHING), 5.0)\n'
        '        )),\n'
        '        SkillUnlock(SkillType.FARMING, 50, listOf(\n'
        '            Effect.DropRateBoost(EffectScope.SingleSkill(SkillType.FARMING), 10.0),\n'
        '            Effect.XpBoost(EffectScope.SingleSkill(SkillType.FARMING), 5.0)\n'
        '        )),\n'
        '        SkillUnlock(SkillType.THIEVING, 50, listOf(\n'
        '            Effect.DropRateBoost(EffectScope.SingleSkill(SkillType.THIEVING), 10.0),\n'
        '            Effect.XpBoost(EffectScope.SingleSkill(SkillType.THIEVING), 5.0)\n'
        '        )),\n'
        '        SkillUnlock(SkillType.SMITHING, 50, listOf(\n'
        '            Effect.MaterialSaveChance(EffectScope.SingleSkill(SkillType.SMITHING), 10.0),\n'
        '            Effect.XpBoost(EffectScope.SingleSkill(SkillType.SMITHING), 5.0)\n'
        '        )),\n'
        '        SkillUnlock(SkillType.COOKING, 50, listOf(\n'
        '            Effect.CraftSuccessBoost(EffectScope.SingleSkill(SkillType.COOKING), 10.0),\n'
        '            Effect.XpBoost(EffectScope.SingleSkill(SkillType.COOKING), 5.0)\n'
        '        )),\n'
        '        SkillUnlock(SkillType.CRAFTING, 50, listOf(\n'
        '            Effect.MaterialSaveChance(EffectScope.SingleSkill(SkillType.CRAFTING), 10.0),\n'
        '            Effect.XpBoost(EffectScope.SingleSkill(SkillType.CRAFTING), 5.0)\n'
        '        )),\n'
        '        SkillUnlock(SkillType.FLETCHING, 50, listOf(\n'
        '            Effect.MaterialSaveChance(EffectScope.SingleSkill(SkillType.FLETCHING), 10.0),\n'
        '            Effect.XpBoost(EffectScope.SingleSkill(SkillType.FLETCHING), 5.0)\n'
        '        )),\n'
        '        SkillUnlock(SkillType.ALCHEMY, 50, listOf(\n'
        '            Effect.MaterialSaveChance(EffectScope.SingleSkill(SkillType.ALCHEMY), 10.0),\n'
        '            Effect.XpBoost(EffectScope.SingleSkill(SkillType.ALCHEMY), 5.0)\n'
        '        ))\n'
        '    )'
    ),
    already_applied_marker="Mastery perks (level 50, one per skill)",
)

# =======================================================================
# 2. ItemsEquipmentSystem.kt - craftOnce() + CraftingSuccessCalculator
# =======================================================================
ies_path = os.path.join(ROOT, "ItemsEquipmentSystem.kt")

guarded_replace(
    ies_path,
    old=(
        '    fun successChancePercent(playerSkillLevel: Int, recipe: Recipe): Double {\n'
        '        val levelsAbove = (playerSkillLevel - recipe.levelRequired).coerceAtLeast(0)\n'
        '        val chance = BASE_SUCCESS_PERCENT + (levelsAbove * PERCENT_PER_LEVEL_ABOVE)\n'
        '        return chance.coerceAtMost(100.0)\n'
        '    }\n'
        '\n'
        '    fun rollSuccess(playerSkillLevel: Int, recipe: Recipe): Boolean {\n'
        '        val chance = successChancePercent(playerSkillLevel, recipe)\n'
        '        return Random.nextDouble(0.0, 100.0) < chance\n'
        '    }\n'
    ),
    new=(
        '    fun successChancePercent(playerSkillLevel: Int, recipe: Recipe, bonusPercent: Double = 0.0): Double {\n'
        '        val levelsAbove = (playerSkillLevel - recipe.levelRequired).coerceAtLeast(0)\n'
        '        val chance = BASE_SUCCESS_PERCENT + (levelsAbove * PERCENT_PER_LEVEL_ABOVE) + bonusPercent\n'
        '        return chance.coerceAtMost(100.0)\n'
        '    }\n'
        '\n'
        '    fun rollSuccess(playerSkillLevel: Int, recipe: Recipe, bonusPercent: Double = 0.0): Boolean {\n'
        '        val chance = successChancePercent(playerSkillLevel, recipe, bonusPercent)\n'
        '        return Random.nextDouble(0.0, 100.0) < chance\n'
        '    }\n'
    ),
    already_applied_marker="fun successChancePercent(playerSkillLevel: Int, recipe: Recipe, bonusPercent",
)

guarded_replace(
    ies_path,
    old=(
        '    fun craftOnce(inventory: Inventory, itemId: String, playerSkillLevel: Int): ServiceResult<CraftingResult> {\n'
        '        val recipe = RecipeCatalog.forOutput(itemId) ?: return ServiceResult.Failure("No recipe for this item.")\n'
        '        if (playerSkillLevel < recipe.levelRequired) {\n'
        '            return ServiceResult.Failure("Requires " + recipe.skillRequired + " level " + recipe.levelRequired + ".")\n'
        '        }\n'
        '\n'
        '        for (ingredient in recipe.ingredients) {\n'
        '            if (inventory.quantityOf(ingredient.itemId) < ingredient.quantity) {\n'
        '                return ServiceResult.Failure("Missing materials: " + ingredient.itemId)\n'
        '            }\n'
        '        }\n'
        '\n'
        '        for (ingredient in recipe.ingredients) {\n'
        '            inventory.removeItem(ingredient.itemId, ingredient.quantity)\n'
        '        }\n'
        '\n'
        '        val succeeded = CraftingSuccessCalculator.rollSuccess(playerSkillLevel, recipe)\n'
        '        if (succeeded) {\n'
        '            inventory.addItem(recipe.outputItemId, recipe.outputQuantity)\n'
        '        }\n'
        '        // Materials are consumed even on failure, per your confirmed design decision.\n'
        '\n'
        '        return ServiceResult.Success(CraftingResult(succeeded, itemId, if (succeeded) recipe.outputQuantity else 0))\n'
        '    }\n'
    ),
    new=(
        '    fun craftOnce(\n'
        '        inventory: Inventory,\n'
        '        itemId: String,\n'
        '        playerSkillLevel: Int,\n'
        '        materialSaveChancePercent: Double = 0.0,\n'
        '        successBonusPercent: Double = 0.0\n'
        '    ): ServiceResult<CraftingResult> {\n'
        '        val recipe = RecipeCatalog.forOutput(itemId) ?: return ServiceResult.Failure("No recipe for this item.")\n'
        '        if (playerSkillLevel < recipe.levelRequired) {\n'
        '            return ServiceResult.Failure("Requires " + recipe.skillRequired + " level " + recipe.levelRequired + ".")\n'
        '        }\n'
        '\n'
        '        for (ingredient in recipe.ingredients) {\n'
        '            if (inventory.quantityOf(ingredient.itemId) < ingredient.quantity) {\n'
        '                return ServiceResult.Failure("Missing materials: " + ingredient.itemId)\n'
        '            }\n'
        '        }\n'
        '\n'
        '        // Mastery Perk (Smithing/Crafting/Fletching/Alchemy): each ingredient\n'
        '        // independently has a chance to not be consumed, rather than one\n'
        '        // all-or-nothing roll for the whole craft.\n'
        '        for (ingredient in recipe.ingredients) {\n'
        '            val saved = materialSaveChancePercent > 0.0 && Random.nextDouble(0.0, 100.0) < materialSaveChancePercent\n'
        '            if (!saved) {\n'
        '                inventory.removeItem(ingredient.itemId, ingredient.quantity)\n'
        '            }\n'
        '        }\n'
        '\n'
        '        val succeeded = CraftingSuccessCalculator.rollSuccess(playerSkillLevel, recipe, successBonusPercent)\n'
        '        if (succeeded) {\n'
        '            inventory.addItem(recipe.outputItemId, recipe.outputQuantity)\n'
        '        }\n'
        '        // Materials are consumed even on failure, per your confirmed design decision.\n'
        '\n'
        '        return ServiceResult.Success(CraftingResult(succeeded, itemId, if (succeeded) recipe.outputQuantity else 0))\n'
        '    }\n'
    ),
    already_applied_marker="materialSaveChancePercent: Double = 0.0,",
)

# =======================================================================
# 3. SharedTypes.kt - 16 cape ItemDefinitions
# =======================================================================
st_path = os.path.join(ROOT, "SharedTypes.kt")

CAPE_SKILLS = [
    "MINING", "WOODCUTTING", "FISHING", "FARMING", "THIEVING",
    "SMITHING", "COOKING", "CRAFTING", "FLETCHING", "ALCHEMY",
    "MAGIC", "ATTACK", "STRENGTH", "DEFENSE", "PRAYER", "ARCHERY",
]


def display_name(skill):
    return skill.capitalize()


cape_defs = []
for skill in CAPE_SKILLS:
    item_id = skill.lower() + "_cape"
    name = display_name(skill) + " Cape"
    cape_defs.append(
        '        ItemDefinition(\n'
        f'            id = "{item_id}", name = "{name}", category = ItemCategory.ARMOR,\n'
        '            rarity = Rarity.LEGENDARY, isTradeable = false, isStackable = false,\n'
        f'            equipSlot = EquipSlot.CAPE, levelRequired = 99, skillRequired = "{skill}"\n'
        '        )'
    )
cape_defs_block = ",\n".join(cape_defs)

guarded_replace(
    st_path,
    old=(
        '        ItemDefinition(\n'
        '            id = "smiths_hammer", name = "Smith\'s Hammer", category = ItemCategory.WEAPON,\n'
        '            rarity = Rarity.UNCOMMON, isTradeable = false, isStackable = false,\n'
        '            equipSlot = EquipSlot.WEAPON, combatStyle = CombatStyle.MELEE, levelRequired = 1,\n'
        '            stats = ItemStats(attackBonus = 2, maxHitBonus = 2)\n'
        '        )\n'
        '   ) + GeneratedItemCatalog.definitions + MetalTierItemCatalog.definitions'
    ),
    new=(
        '        ItemDefinition(\n'
        '            id = "smiths_hammer", name = "Smith\'s Hammer", category = ItemCategory.WEAPON,\n'
        '            rarity = Rarity.UNCOMMON, isTradeable = false, isStackable = false,\n'
        '            equipSlot = EquipSlot.WEAPON, combatStyle = CombatStyle.MELEE, levelRequired = 1,\n'
        '            stats = ItemStats(attackBonus = 2, maxHitBonus = 2)\n'
        '        ),\n'
        f'{cape_defs_block}\n'
        '   ) + GeneratedItemCatalog.definitions + MetalTierItemCatalog.definitions'
    ),
    already_applied_marker='id = "mining_cape"',
)

# =======================================================================
# 4. MarketScreen.kt - VendorBuyCatalog gets the 16 capes
# =======================================================================
ms_path = os.path.join(ROOT, "MarketScreen.kt")

vendor_entries = ",\n".join(
    f'        VendorBuyableItem("{skill.lower()}_cape", "{display_name(skill)} Cape", 10000L)'
    for skill in CAPE_SKILLS
)

guarded_replace(
    ms_path,
    old=(
        'object VendorBuyCatalog {\n'
        '    val items = listOf(\n'
        '        VendorBuyableItem("flour", "Flour", 2L),\n'
        '        VendorBuyableItem("vial_of_water", "Vial of Water", 2L)\n'
        '    )\n'
        '}'
    ),
    new=(
        'object VendorBuyCatalog {\n'
        '    val items = listOf(\n'
        '        VendorBuyableItem("flour", "Flour", 2L),\n'
        '        VendorBuyableItem("vial_of_water", "Vial of Water", 2L),\n'
        f'{vendor_entries}\n'
        '    )\n'
        '}'
    ),
    already_applied_marker='VendorBuyableItem("mining_cape"',
)

# =======================================================================
# 5. MainActivity.kt - effect display branches + vendor call site
# =======================================================================
ma_path = os.path.join(ROOT, "MainActivity.kt")

guarded_replace(
    ma_path,
    old='    is Effect.TimerReduction -> "-" + effect.percent + "% action time"\n}',
    new=(
        '    is Effect.TimerReduction -> "-" + effect.percent + "% action time"\n'
        '    is Effect.MaterialSaveChance -> "+" + effect.percent + "% material save chance"\n'
        '    is Effect.CraftSuccessBoost -> "+" + effect.percent + "% success chance"\n'
        '}'
    ),
    already_applied_marker="is Effect.MaterialSaveChance ->",
)

guarded_replace(
    ma_path,
    old="vendorBuyableItems = VendorBuyCatalog.items,",
    new="vendorBuyableItems = gameViewModel.vendorBuyableItems(),",
    already_applied_marker="vendorBuyableItems = gameViewModel.vendorBuyableItems(),",
)

# =======================================================================
# 6. GameViewModel.kt - imports, cape bonus effects, combat/gathering/
#    crafting mastery hooks, vendor level-gating
# =======================================================================
gvm_path = os.path.join(ROOT, "GameViewModel.kt")

# 6a. Defensive imports for symbols not previously referenced in this file
guarded_replace(
    gvm_path,
    old="import com.yourname.idlerpg.SupabaseLeaderboardRepository\n",
    new=(
        "import com.yourname.idlerpg.SupabaseLeaderboardRepository\n"
        "import com.yourname.idlerpg.UnlockTable\n"
        "import com.yourname.idlerpg.EffectStacker\n"
        "import com.yourname.idlerpg.VendorBuyCatalog\n"
        "import com.yourname.idlerpg.VendorBuyableItem\n"
    ),
    already_applied_marker="import com.yourname.idlerpg.UnlockTable\n",
)

# 6b. New helper functions: capeItemIdFor, hasSkillCapeEquipped,
#     masteryBonusPercent, capeBonusEffects, vendorBuyableItems.
#     Inserted right after guildXpBonusEffects() (same section, same pattern).
guarded_replace(
    gvm_path,
    old=(
        "        return SkillGroup.entries.map { group -> Effect.XpBoost(EffectScope.Group(group), percent) }\n"
        "    }\n"
    ),
    new=(
        "        return SkillGroup.entries.map { group -> Effect.XpBoost(EffectScope.Group(group), percent) }\n"
        "    }\n"
        "\n"
        "    // =========================================================\n"
        "    // MASTERY PERKS + SKILL CAPES\n"
        "    // Level-50 perks live in UnlockTable (existing level->effect\n"
        "    // mechanism). Capes add an equal-sized extra bonus on top while\n"
        "    // worn, mirroring the guild XP bonus pattern above: extra Effects\n"
        "    // merged in at every grantXp() call site via capeBonusEffects().\n"
        "    // Combat's hit-chance/damage/reduction bonuses are NOT routed\n"
        "    // through the Effect system (combat's accuracy/damage formulas\n"
        "    // are already hardcoded, not effect-driven) - those use direct\n"
        "    // level/cape checks via masteryBonusPercent() instead.\n"
        "    // =========================================================\n"
        "    private fun capeItemIdFor(skillType: SkillType): String = skillType.name.lowercase() + \"_cape\"\n"
        "\n"
        "    private fun hasSkillCapeEquipped(characterId: String, skillType: SkillType): Boolean =\n"
        "        inventoryService.inventoryFor(characterId).equippedItemIn(EquipSlot.CAPE) == capeItemIdFor(skillType)\n"
        "\n"
        "    private fun masteryBonusPercent(level: Int, hasCape: Boolean, baseBonus: Double, capeBonus: Double): Double = when {\n"
        "        hasCape -> capeBonus\n"
        "        level >= 50 -> baseBonus\n"
        "        else -> 0.0\n"
        "    }\n"
        "\n"
        "    private fun capeBonusEffects(characterId: String): List<Effect> {\n"
        "        val equippedCapeId = inventoryService.inventoryFor(characterId).equippedItemIn(EquipSlot.CAPE) ?: return emptyList()\n"
        "        val skill = SkillType.values().find { capeItemIdFor(it) == equippedCapeId } ?: return emptyList()\n"
        "        val xpBoost = Effect.XpBoost(EffectScope.SingleSkill(skill), 5.0)\n"
        "        val specific: Effect? = when (skill) {\n"
        "            SkillType.MINING, SkillType.WOODCUTTING, SkillType.FISHING, SkillType.FARMING, SkillType.THIEVING ->\n"
        "                Effect.DropRateBoost(EffectScope.SingleSkill(skill), 10.0)\n"
        "            SkillType.SMITHING, SkillType.CRAFTING, SkillType.FLETCHING, SkillType.ALCHEMY ->\n"
        "                Effect.MaterialSaveChance(EffectScope.SingleSkill(skill), 10.0)\n"
        "            SkillType.COOKING -> Effect.CraftSuccessBoost(EffectScope.SingleSkill(skill), 10.0)\n"
        "            else -> null // combat skills: handled directly via hasSkillCapeEquipped() in tickCombat\n"
        "        }\n"
        "        return listOfNotNull(xpBoost, specific)\n"
        "    }\n"
        "\n"
        "    fun vendorBuyableItems(): List<VendorBuyableItem> {\n"
        "        val characterId = _currentCharacterId.value\n"
        "        return VendorBuyCatalog.items.filter { vendorItem ->\n"
        "            val def = ItemCatalog.find(vendorItem.itemId)\n"
        "            val requiredSkillName = def?.skillRequired\n"
        "            if (requiredSkillName == null || characterId == null) {\n"
        "                true\n"
        "            } else {\n"
        "                val skillType = SkillType.values().find { it.name == requiredSkillName }\n"
        "                if (skillType == null) true else skillLevel(characterId, skillType) >= (def.levelRequired)\n"
        "            }\n"
        "        }\n"
        "    }\n"
    ),
    already_applied_marker="MASTERY PERKS + SKILL CAPES",
)

# 6c. Thread capeBonusEffects() into all 3 grantXp() call sites
#     (same call sites the guild XP bonus already covers).
guarded_replace(
    gvm_path,
    old="progressionService.grantXp(characterId, skillType, action.xpPerAction * effectiveActions, guildXpBonusEffects())",
    new="progressionService.grantXp(characterId, skillType, action.xpPerAction * effectiveActions, guildXpBonusEffects() + capeBonusEffects(characterId))",
    already_applied_marker="action.xpPerAction * effectiveActions, guildXpBonusEffects() + capeBonusEffects",
)

guarded_replace(
    gvm_path,
    old="val xpGrant = progressionService.grantXp(characterId, trainingSkill, (attack.damageDealt * 4 + 5).toLong(), guildXpBonusEffects())",
    new="val xpGrant = progressionService.grantXp(characterId, trainingSkill, (attack.damageDealt * 4 + 5).toLong(), guildXpBonusEffects() + capeBonusEffects(characterId))",
    already_applied_marker="(attack.damageDealt * 4 + 5).toLong(), guildXpBonusEffects() + capeBonusEffects",
)

guarded_replace(
    gvm_path,
    old="            progressionService.grantXp(characterId, skillType, xpGranted, guildXpBonusEffects())\n        }\n        return CraftBatchResult(successes, totalProduced, xpGranted, stoppedReason)",
    new="            progressionService.grantXp(characterId, skillType, xpGranted, guildXpBonusEffects() + capeBonusEffects(characterId))\n        }\n        return CraftBatchResult(successes, totalProduced, xpGranted, stoppedReason)",
    already_applied_marker="xpGranted, guildXpBonusEffects() + capeBonusEffects(characterId))\n        }\n        return CraftBatchResult",
)

# 6d. Gathering: wire DropRateBoost into tickSkilling's per-action grant
guarded_replace(
    gvm_path,
    old=(
        "                progressionService.grantXp(characterId, skillType, action.xpPerAction * effectiveActions, guildXpBonusEffects() + capeBonusEffects(characterId))\n"
        "                inventory.addItem(queue.itemId, effectiveActions.toInt())\n"
        "                if (skillType == SkillType.MINING) {\n"
        "                    MiningBonusGemTable.rollAndGrant(inventory, effectiveActions.toInt())\n"
        "                }\n"
    ),
    new=(
        "                progressionService.grantXp(characterId, skillType, action.xpPerAction * effectiveActions, guildXpBonusEffects() + capeBonusEffects(characterId))\n"
        "                inventory.addItem(queue.itemId, effectiveActions.toInt())\n"
        "                if (skillType == SkillType.MINING) {\n"
        "                    MiningBonusGemTable.rollAndGrant(inventory, effectiveActions.toInt())\n"
        "                }\n"
        "                // Mastery Perk (gathering skills): chance of one bonus item per\n"
        "                // completed action, rolled independently per action.\n"
        "                val gatherBook = progressionService.skillBookFor(characterId)\n"
        "                val gatherActiveEffects = UnlockTable.allActiveEffects(gatherBook) + capeBonusEffects(characterId)\n"
        "                val dropRateBoostPercent = EffectStacker.totalDropRateBoostPercent(gatherActiveEffects, skillType)\n"
        "                if (dropRateBoostPercent > 0.0) {\n"
        "                    var bonusCount = 0\n"
        "                    repeat(effectiveActions.toInt()) {\n"
        "                        if (Random.nextDouble(0.0, 100.0) < dropRateBoostPercent) bonusCount++\n"
        "                    }\n"
        "                    if (bonusCount > 0) inventory.addItem(queue.itemId, bonusCount)\n"
        "                }\n"
    ),
    already_applied_marker="Mastery Perk (gathering skills): chance of one bonus item",
)

# 6e. Crafting: thread materialSaveChancePercent / successBonusPercent
guarded_replace(
    gvm_path,
    old=(
        '        var successes = 0\n'
        '        var totalProduced = 0\n'
        '        var xpGranted = 0L\n'
        '        var stoppedReason: String? = null\n'
        '        for (i in 0 until attempts) {\n'
        '            val result = craftingService.craftOnce(inventory, itemId, playerLevel)\n'
    ),
    new=(
        '        val craftActiveEffects = UnlockTable.allActiveEffects(book) + capeBonusEffects(characterId)\n'
        '        val materialSaveChancePercent = EffectStacker.totalMaterialSaveChancePercent(craftActiveEffects, skillType)\n'
        '        val successBonusPercent = EffectStacker.totalCraftSuccessBoostPercent(craftActiveEffects, skillType)\n'
        '\n'
        '        var successes = 0\n'
        '        var totalProduced = 0\n'
        '        var xpGranted = 0L\n'
        '        var stoppedReason: String? = null\n'
        '        for (i in 0 until attempts) {\n'
        '            val result = craftingService.craftOnce(inventory, itemId, playerLevel, materialSaveChancePercent, successBonusPercent)\n'
    ),
    already_applied_marker="val materialSaveChancePercent = EffectStacker.totalMaterialSaveChancePercent",
)

# 6f. Combat: MAGIC branch mastery bonus
guarded_replace(
    gvm_path,
    old=(
        '            CombatStyle.MAGIC -> {\n'
        '                val magicLevel = skillLevel(characterId, SkillType.MAGIC)\n'
        '                accuracy = magicLevel * 2 + weapon.baseAccuracy\n'
        '                maxHit = (magicLevel / 3) + weapon.baseMaxHit\n'
        '                minHit = magicLevel / 10\n'
        '                attackSpeedSeconds = weapon.attackSpeedSeconds\n'
        '            }\n'
    ),
    new=(
        '            CombatStyle.MAGIC -> {\n'
        '                val magicLevel = skillLevel(characterId, SkillType.MAGIC)\n'
        '                val magicMastery = masteryBonusPercent(magicLevel, hasSkillCapeEquipped(characterId, SkillType.MAGIC), 5.0, 10.0)\n'
        '                accuracy = ((magicLevel * 2 + weapon.baseAccuracy) * (1.0 + magicMastery / 100.0)).toInt()\n'
        '                maxHit = (magicLevel / 3) + weapon.baseMaxHit\n'
        '                minHit = magicLevel / 10\n'
        '                attackSpeedSeconds = weapon.attackSpeedSeconds\n'
        '            }\n'
    ),
    already_applied_marker="val magicMastery = masteryBonusPercent",
)

# 6g. Combat: RANGED branch mastery bonus
guarded_replace(
    gvm_path,
    old=(
        '            CombatStyle.RANGED -> {\n'
        '                val archeryLevel = skillLevel(characterId, SkillType.ARCHERY)\n'
        '                accuracy = archeryLevel * 2 + weapon.baseAccuracy\n'
        '                maxHit = (archeryLevel / 3) + weapon.baseMaxHit\n'
        '                minHit = archeryLevel / 10\n'
        '                attackSpeedSeconds = weapon.attackSpeedSeconds\n'
        '            }\n'
    ),
    new=(
        '            CombatStyle.RANGED -> {\n'
        '                val archeryLevel = skillLevel(characterId, SkillType.ARCHERY)\n'
        '                val archeryMastery = masteryBonusPercent(archeryLevel, hasSkillCapeEquipped(characterId, SkillType.ARCHERY), 5.0, 10.0)\n'
        '                accuracy = ((archeryLevel * 2 + weapon.baseAccuracy) * (1.0 + archeryMastery / 100.0)).toInt()\n'
        '                maxHit = (archeryLevel / 3) + weapon.baseMaxHit\n'
        '                minHit = archeryLevel / 10\n'
        '                attackSpeedSeconds = weapon.attackSpeedSeconds\n'
        '            }\n'
    ),
    already_applied_marker="val archeryMastery = masteryBonusPercent",
)

# 6h. Combat: MELEE (else) branch mastery bonus
guarded_replace(
    gvm_path,
    old=(
        '            else -> {\n'
        '                val attackLevel = skillLevel(characterId, SkillType.ATTACK)\n'
        '                val strengthLevel = skillLevel(characterId, SkillType.STRENGTH)\n'
        '                accuracy = attackLevel * 2 + (weapon?.baseAccuracy ?: 5)\n'
        '                maxHit = (strengthLevel / 3) + (weapon?.baseMaxHit ?: 1)\n'
        '                minHit = strengthLevel / 10\n'
        '                attackSpeedSeconds = weapon?.attackSpeedSeconds ?: 2.4\n'
        '            }\n'
    ),
    new=(
        '            else -> {\n'
        '                val attackLevel = skillLevel(characterId, SkillType.ATTACK)\n'
        '                val strengthLevel = skillLevel(characterId, SkillType.STRENGTH)\n'
        '                val attackMastery = masteryBonusPercent(attackLevel, hasSkillCapeEquipped(characterId, SkillType.ATTACK), 5.0, 10.0)\n'
        '                val strengthMastery = masteryBonusPercent(strengthLevel, hasSkillCapeEquipped(characterId, SkillType.STRENGTH), 5.0, 10.0)\n'
        '                accuracy = ((attackLevel * 2 + (weapon?.baseAccuracy ?: 5)) * (1.0 + attackMastery / 100.0)).toInt()\n'
        '                maxHit = (((strengthLevel / 3) + (weapon?.baseMaxHit ?: 1)) * (1.0 + strengthMastery / 100.0)).toInt()\n'
        '                minHit = ((strengthLevel / 10) * (1.0 + strengthMastery / 100.0)).toInt()\n'
        '                attackSpeedSeconds = weapon?.attackSpeedSeconds ?: 2.4\n'
        '            }\n'
    ),
    already_applied_marker="val attackMastery = masteryBonusPercent",
)

# 6i. Combat: Defense mastery bonus on the reduction formula
guarded_replace(
    gvm_path,
    old=(
        "                    val defenseLevel = skillLevel(characterId, SkillType.DEFENSE)\n"
        "                    val defenseReductionPercent = (defenseLevel * 0.5).coerceAtMost(50.0)\n"
    ),
    new=(
        "                    val defenseLevel = skillLevel(characterId, SkillType.DEFENSE)\n"
        "                    val defenseMastery = masteryBonusPercent(defenseLevel, hasSkillCapeEquipped(characterId, SkillType.DEFENSE), 5.0, 10.0)\n"
        "                    val defenseReductionPercent = (defenseLevel * 0.5 + defenseMastery).coerceAtMost(50.0)\n"
    ),
    already_applied_marker="val defenseMastery = masteryBonusPercent",
)

# 6j. Combat: Prayer mastery bonus (extra reduction whenever any prayer is active)
guarded_replace(
    gvm_path,
    old=(
        "                    val prayerAdjustedDmg = if (inventoryService.inventoryFor(characterId).selectedPrayerId == \"rock_skin\") {\n"
        "                        (rawDmg * 0.8).toInt().coerceAtLeast(1)\n"
        "                    } else {\n"
        "                        rawDmg\n"
        "                    }\n"
    ),
    new=(
        "                    val activePrayerId = inventoryService.inventoryFor(characterId).selectedPrayerId\n"
        "                    val prayerSpecificDmg = if (activePrayerId == \"rock_skin\") {\n"
        "                        (rawDmg * 0.8).toInt().coerceAtLeast(1)\n"
        "                    } else {\n"
        "                        rawDmg\n"
        "                    }\n"
        "                    // Mastery Perk (Prayer): extra reduction whenever ANY prayer is\n"
        "                    // active, stacking on top of that prayer's own specific effect.\n"
        "                    val prayerMasteryReductionPercent = if (activePrayerId != null) {\n"
        "                        val prayerLevel = skillLevel(characterId, SkillType.PRAYER)\n"
        "                        masteryBonusPercent(prayerLevel, hasSkillCapeEquipped(characterId, SkillType.PRAYER), 5.0, 10.0)\n"
        "                    } else {\n"
        "                        0.0\n"
        "                    }\n"
        "                    val prayerAdjustedDmg = (prayerSpecificDmg * (1.0 - prayerMasteryReductionPercent / 100.0)).toInt().coerceAtLeast(1)\n"
    ),
    already_applied_marker="Mastery Perk (Prayer): extra reduction whenever ANY prayer",
)

print("\nAll mastery perk + skill cape patches applied successfully.")
