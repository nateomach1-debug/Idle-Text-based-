item_path = "app/src/main/kotlin/com/yourname/idlerpg/GeneratedItemCatalog.kt"
with open(item_path, encoding="utf-8") as f:
    content = f.read()

anchor_bone_item = '''    ItemDefinition(
        id = "bone",
        name = "Bone",
        category = ItemCategory.MATERIAL,
        isTradeable = true,
        isStackable = true
    ),'''
count = content.count(anchor_bone_item)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(anchor_bone_item, anchor_bone_item + '''
    ItemDefinition(
        id = "gem_bones",
        name = "Gem Bones",
        category = ItemCategory.MATERIAL,
        isTradeable = true,
        isStackable = true
    ),
    ItemDefinition(
        id = "big_bones",
        name = "Big Bones",
        category = ItemCategory.MATERIAL,
        isTradeable = true,
        isStackable = true
    ),
    ItemDefinition(
        id = "dragon_bones",
        name = "Dragon Bones",
        category = ItemCategory.MATERIAL,
        isTradeable = true,
        isStackable = true
    ),''', 1)

anchor_bone_price = '    "bone" to 2L,'
count = content.count(anchor_bone_price)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(anchor_bone_price, anchor_bone_price + '''
    "gem_bones" to 25L,
    "big_bones" to 15L,
    "dragon_bones" to 100L,''', 1)

with open(item_path, "w", encoding="utf-8") as f:
    f.write(content)

combat_path = "app/src/main/kotlin/com/yourname/idlerpg/CombatSystem.kt"
with open(combat_path, encoding="utf-8") as f:
    content = f.read()

anchor_old_bone_drop = '                        LootEntry("bone", 1, 1, 60.0),\n'
count = content.count(anchor_old_bone_drop)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(anchor_old_bone_drop, '', 1)

anchor_rollLoot = '''    private fun rollLoot(state: CharacterCombatState, monster: Monster) {
        (monster.mainLootTable + monster.rareLootTable).forEach { entry ->
            if (Random.nextDouble(0.0, 100.0) < entry.dropChancePercent) {
                val qty = Random.nextInt(entry.minQty, entry.maxQty + 1)
                state.lootPool.add(entry.copy(minQty = qty, maxQty = qty))
            }
        }
        state.pendingCoins += CoinDropTable.rollCoins(monster.levelRequirement)
    }'''
count = content.count(anchor_rollLoot)
assert count == 1, f"Expected 1 match, found {count}."
replacement_rollLoot = '''    private fun rollLoot(state: CharacterCombatState, monster: Monster) {
        (monster.mainLootTable + monster.rareLootTable).forEach { entry ->
            if (Random.nextDouble(0.0, 100.0) < entry.dropChancePercent) {
                val qty = Random.nextInt(entry.minQty, entry.maxQty + 1)
                state.lootPool.add(entry.copy(minQty = qty, maxQty = qty))
            }
        }
        // Every monster guarantees exactly 1 bone per kill, tiered by monster level.
        val boneType = when {
            monster.levelRequirement >= 60 -> "dragon_bones"
            monster.levelRequirement >= 20 -> "big_bones"
            monster.levelRequirement >= 15 -> "gem_bones"
            else -> "bone"
        }
        state.lootPool.add(LootEntry(boneType, 1, 1, 100.0))
        state.pendingCoins += CoinDropTable.rollCoins(monster.levelRequirement)
    }'''
content = content.replace(anchor_rollLoot, replacement_rollLoot, 1)

with open(combat_path, "w", encoding="utf-8") as f:
    f.write(content)

action_path = "app/src/main/kotlin/com/yourname/idlerpg/ActionCatalog.kt"
with open(action_path, encoding="utf-8") as f:
    content = f.read()

anchor_farming_map_end = '''    "lemon" to "lemon_sapling",
    "pumpkin" to "pumpkin_seed"
)'''
count = content.count(anchor_farming_map_end)
assert count == 1, f"Expected 1 match, found {count}."
content = content.replace(anchor_farming_map_end, anchor_farming_map_end + '''

data class BoneBuryInfo(val levelRequired: Int, val xpAmount: Long)

// Bury Bones (an instant Prayer-training action, not a queued skill action -
// Prayer is deliberately excluded from the normal training-skill picker).
// Level requirements increase strictly with the tier's source monster level.
val PrayerBoneRequirements: Map<String, BoneBuryInfo> = mapOf(
    "bone" to BoneBuryInfo(1, 5),
    "gem_bones" to BoneBuryInfo(15, 15),
    "big_bones" to BoneBuryInfo(25, 25),
    "dragon_bones" to BoneBuryInfo(50, 72)
)''', 1)

with open(action_path, "w", encoding="utf-8") as f:
    f.write(content)

gvm_path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
with open(gvm_path, encoding="utf-8") as f:
    content = f.read()

anchor_useItem = '''    fun useInventoryItem(itemId: String) {
        val characterId = _currentCharacterId.value ?: return
        val definition = ItemCatalog.find(itemId) ?: return
        if (definition.consumableType != ConsumableType.FOOD) return
        val inventory = inventoryService.inventoryFor(characterId)
        val removed = inventory.removeItem(itemId, 1)
        if (removed is ServiceResult.Success) {
            combatService.healCharacter(characterId, definition.healAmount ?: 0)
            refreshInventory()
        }
    }'''
count = content.count(anchor_useItem)
assert count == 1, f"Expected 1 match, found {count}."
replacement_useItem = anchor_useItem + '''

    fun buryBone(itemId: String) {
        val characterId = _currentCharacterId.value ?: return
        val boneInfo = PrayerBoneRequirements[itemId] ?: return
        val prayerLevel = skillLevel(characterId, SkillType.PRAYER)
        if (prayerLevel < boneInfo.levelRequired) return
        val inventory = inventoryService.inventoryFor(characterId)
        val removed = inventory.removeItem(itemId, 1)
        if (removed is ServiceResult.Success) {
            progressionService.grantXp(characterId, SkillType.PRAYER, boneInfo.xpAmount)
            refreshInventory()
            refreshSkills()
        }
    }'''
content = content.replace(anchor_useItem, replacement_useItem, 1)

with open(gvm_path, "w", encoding="utf-8") as f:
    f.write(content)

inv_path = "app/src/main/kotlin/com/yourname/idlerpg/InventoryScreen.kt"
with open(inv_path, encoding="utf-8") as f:
    content = f.read()

anchor_summary = '''data class InventoryItemSummary(
    val itemId: String,
    val displayName: String,
    val category: InventoryCategory,
    val quantity: Int,
    val isEquippable: Boolean,
    val isConsumable: Boolean,
    val npcValuePerUnit: Long,
    val statsDescription: String? = null // e.g. "ATK +5, ACC +10" -- only for equippable items
)'''
count = content.count(anchor_summary)
assert count == 1, f"Expected 1 match, found {count}."
replacement_summary = '''data class InventoryItemSummary(
    val itemId: String,
    val displayName: String,
    val category: InventoryCategory,
    val quantity: Int,
    val isEquippable: Boolean,
    val isConsumable: Boolean,
    val npcValuePerUnit: Long,
    val statsDescription: String? = null, // e.g. "ATK +5, ACC +10" -- only for equippable items
    val isBuryable: Boolean = false
)'''
content = content.replace(anchor_summary, replacement_summary, 1)

anchor_screen_sig = '''@Composable
fun InventoryScreen(
    items: List<InventoryItemSummary>,
    onOpenEquipment: () -> Unit,
    onOpenLoadout: () -> Unit,
    onUseItem: (String) -> Unit,
    onSellOnMarket: (String) -> Unit,
    onEquipItem: (String) -> Unit,
    canEquip: (InventoryItemSummary) -> Pair<Boolean, String?>, // (canEquip, lockReasonIfNot)
    modifier: Modifier = Modifier
) {'''
count = content.count(anchor_screen_sig)
assert count == 1, f"Expected 1 match, found {count}."
replacement_screen_sig = '''@Composable
fun InventoryScreen(
    items: List<InventoryItemSummary>,
    onOpenEquipment: () -> Unit,
    onOpenLoadout: () -> Unit,
    onUseItem: (String) -> Unit,
    onSellOnMarket: (String) -> Unit,
    onEquipItem: (String) -> Unit,
    onBuryItem: (String) -> Unit,
    canEquip: (InventoryItemSummary) -> Pair<Boolean, String?>, // (canEquip, lockReasonIfNot)
    canBury: (InventoryItemSummary) -> Pair<Boolean, String?>, // (canBury, lockReasonIfNot)
    modifier: Modifier = Modifier
) {'''
content = content.replace(anchor_screen_sig, replacement_screen_sig, 1)

anchor_sheet_call = '''    selectedItem?.let { item ->
        ItemActionSheet(
            item = item,
            canEquip = canEquip(item),
            onUse = { onUseItem(item.itemId); selectedItem = null },
            onSell = { onSellOnMarket(item.itemId); selectedItem = null },
            onEquip = { onEquipItem(item.itemId); selectedItem = null },
            onDismiss = { selectedItem = null }
        )
    }'''
count = content.count(anchor_sheet_call)
assert count == 1, f"Expected 1 match, found {count}."
replacement_sheet_call = '''    selectedItem?.let { item ->
        ItemActionSheet(
            item = item,
            canEquip = canEquip(item),
            canBury = canBury(item),
            onUse = { onUseItem(item.itemId); selectedItem = null },
            onSell = { onSellOnMarket(item.itemId); selectedItem = null },
            onEquip = { onEquipItem(item.itemId); selectedItem = null },
            onBury = { onBuryItem(item.itemId); selectedItem = null },
            onDismiss = { selectedItem = null }
        )
    }'''
content = content.replace(anchor_sheet_call, replacement_sheet_call, 1)

anchor_sheet_sig = '''@Composable
private fun ItemActionSheet(
    item: InventoryItemSummary,
    canEquip: Pair<Boolean, String?>,
    onUse: () -> Unit,
    onSell: () -> Unit,
    onEquip: () -> Unit,
    onDismiss: () -> Unit
) {'''
count = content.count(anchor_sheet_sig)
assert count == 1, f"Expected 1 match, found {count}."
replacement_sheet_sig = '''@Composable
private fun ItemActionSheet(
    item: InventoryItemSummary,
    canEquip: Pair<Boolean, String?>,
    canBury: Pair<Boolean, String?>,
    onUse: () -> Unit,
    onSell: () -> Unit,
    onEquip: () -> Unit,
    onBury: () -> Unit,
    onDismiss: () -> Unit
) {'''
content = content.replace(anchor_sheet_sig, replacement_sheet_sig, 1)

anchor_equip_block_end = '''                    Spacer(modifier = Modifier.height(8.dp))
                }

                OutlinedButton(onClick = onSell, modifier = Modifier.fillMaxWidth()) {
                    Text(text = "Sell on Market")
                }'''
count = content.count(anchor_equip_block_end)
assert count == 1, f"Expected 1 match, found {count}."
replacement_equip_block_end = '''                    Spacer(modifier = Modifier.height(8.dp))
                }

                if (item.isBuryable) {
                    val (canBuryNow, buryLockReason) = canBury
                    Button(
                        onClick = onBury,
                        enabled = canBuryNow,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text(text = "Bury")
                    }
                    if (!canBuryNow && buryLockReason != null) {
                        Spacer(modifier = Modifier.height(4.dp))
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                imageVector = Icons.Filled.Lock,
                                contentDescription = "Locked",
                                tint = MaterialTheme.colorScheme.error,
                                modifier = Modifier.size(14.dp)
                            )
                            Spacer(modifier = Modifier.width(4.dp))
                            Text(text = buryLockReason, style = MaterialTheme.typography.labelSmall)
                        }
                    }
                    Spacer(modifier = Modifier.height(8.dp))
                }

                OutlinedButton(onClick = onSell, modifier = Modifier.fillMaxWidth()) {
                    Text(text = "Sell on Market")
                }'''
content = content.replace(anchor_equip_block_end, replacement_equip_block_end, 1)

with open(inv_path, "w", encoding="utf-8") as f:
    f.write(content)

main_path = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
with open(main_path, encoding="utf-8") as f:
    content = f.read()

anchor_canEquip_fn = '''    fun canEquip(item: InventoryItemSummary): Pair<Boolean, String?> {
        if (item.category == InventoryCategory.TOOL) return true to null
        val locked = combatViewData?.viewState == CombatViewState.IN_COMBAT
        return if (locked) false to "Locked during combat" else true to null
    }'''
count = content.count(anchor_canEquip_fn)
assert count == 1, f"Expected 1 match, found {count}."
replacement_canEquip_fn = anchor_canEquip_fn + '''

    fun canBury(item: InventoryItemSummary): Pair<Boolean, String?> {
        val boneInfo = PrayerBoneRequirements[item.itemId] ?: return false to null
        val prayerLevel = allSkills["PRAYER"]?.level ?: 1
        return if (prayerLevel < boneInfo.levelRequired) {
            false to ("Requires Prayer level " + boneInfo.levelRequired)
        } else {
            true to null
        }
    }'''
content = content.replace(anchor_canEquip_fn, replacement_canEquip_fn, 1)

anchor_inv_summary_real = '''            InventoryItemSummary(
                itemId = entry.itemId,
                displayName = definition.name,
                category = mapItemCategory(definition.category),
                quantity = entry.quantity,
                isEquippable = definition.equipSlot != null,
                isConsumable = definition.category == ItemCategory.CONSUMABLE,
                npcValuePerUnit = vendorPayoutFor(entry.itemId),
                statsDescription = statsText
            )'''
count = content.count(anchor_inv_summary_real)
assert count == 1, f"Expected 1 match, found {count}."
replacement_inv_summary_real = '''            InventoryItemSummary(
                itemId = entry.itemId,
                displayName = definition.name,
                category = mapItemCategory(definition.category),
                quantity = entry.quantity,
                isEquippable = definition.equipSlot != null,
                isConsumable = definition.category == ItemCategory.CONSUMABLE,
                npcValuePerUnit = vendorPayoutFor(entry.itemId),
                statsDescription = statsText,
                isBuryable = PrayerBoneRequirements.containsKey(entry.itemId)
            )'''
content = content.replace(anchor_inv_summary_real, replacement_inv_summary_real, 1)

anchor_inv_call = '''                                    onEquipItem = { itemId -> gameViewModel.equipItem(itemId) },
                                    canEquip = ::canEquip
                                )'''
count = content.count(anchor_inv_call)
assert count == 1, f"Expected 1 match, found {count}."
replacement_inv_call = '''                                    onEquipItem = { itemId -> gameViewModel.equipItem(itemId) },
                                    onBuryItem = { itemId -> gameViewModel.buryBone(itemId) },
                                    canEquip = ::canEquip,
                                    canBury = ::canBury
                                )'''
content = content.replace(anchor_inv_call, replacement_inv_call, 1)

with open(main_path, "w", encoding="utf-8") as f:
    f.write(content)

print("patch_add_bones_and_prayer.py applied cleanly.")
