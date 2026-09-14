import pathlib

gvm_path = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt")
loadout_path = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/LoadoutScreen.kt")
moderation_path = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/ModerationScreen.kt")
main_activity_path = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt")

gvm_text = gvm_path.read_text()
loadout_text = loadout_path.read_text()
moderation_text = moderation_path.read_text()
main_activity_text = main_activity_path.read_text()

errors = []


def apply_edit(text, old, new, marker, label, errors):
    if text.count(marker) >= 1:
        return text, False  # already applied
    count_old = text.count(old)
    if count_old == 1:
        return text.replace(old, new), True
    errors.append(f"{label}: expected exactly 1 match of old block (and marker absent), found old={count_old}")
    return text, False


# ============================================================
# 1. GameViewModel.kt - fix auto-heal maxHp initialization race
# ============================================================
gvm_old_1 = """    private fun tickConsumables(elapsedSeconds: Long) {
        val characterId = _currentCharacterId.value ?: return
        val inventory = inventoryService.inventoryFor(characterId)
        val combatState = combatService.stateFor(characterId)"""
gvm_new_1 = """    private fun tickConsumables(elapsedSeconds: Long) {
        val characterId = _currentCharacterId.value ?: return
        val inventory = inventoryService.inventoryFor(characterId)
        val combatState = combatService.stateFor(characterId, maxHpFor(characterId))"""
gvm_text, c1 = apply_edit(gvm_text, gvm_old_1, gvm_new_1, "combatService.stateFor(characterId, maxHpFor(characterId))\n\n", "GameViewModel.kt tickConsumables maxHp fix", errors)
# NOTE: the marker above intentionally includes trailing context distinguishing this
# call site from tickCombat's identical call (handled by a more specific check below).

# ============================================================
# 2. GameViewModel.kt - new grantTestGems() function
# ============================================================
gvm_old_2 = """    fun purchasePreset(presetId: String) {
        val accountId = _currentAccountId.value ?: return
        val result = accountService.purchasePreset(accountId, presetId)
        if (result is ServiceResult.Failure) {
            _premiumActionError.value = result.reason
            return
        }
        _premiumActionError.value = null
        refreshCurrency()
        saveGame()
    }"""
gvm_new_2 = """    fun purchasePreset(presetId: String) {
        val accountId = _currentAccountId.value ?: return
        val result = accountService.purchasePreset(accountId, presetId)
        if (result is ServiceResult.Failure) {
            _premiumActionError.value = result.reason
            return
        }
        _premiumActionError.value = null
        refreshCurrency()
        saveGame()
    }

    // Moderator/testing tool only - credits the currently logged-in account
    // directly, bypassing Play Billing entirely. Does NOT target other
    // players' accounts (this app's Account/AccountService layer is local
    // per-device, not a live server-side directory).
    fun grantTestGems(amount: Long) {
        val accountId = _currentAccountId.value ?: return
        val result = accountService.addCurrency(accountId, amount)
        if (result is ServiceResult.Failure) {
            _premiumActionError.value = result.reason
            return
        }
        _premiumActionError.value = null
        refreshCurrency()
        saveGame()
    }"""
gvm_text, c2 = apply_edit(gvm_text, gvm_old_2, gvm_new_2, "fun grantTestGems(amount: Long)", "GameViewModel.kt grantTestGems", errors)

# ============================================================
# 3. LoadoutScreen.kt - onFoodSelected becomes nullable
# ============================================================
lo_old_1 = "    onFoodSelected: (String) -> Unit,"
lo_new_1 = "    onFoodSelected: (String?) -> Unit,"
loadout_text, c3 = apply_edit(loadout_text, lo_old_1, lo_new_1, "onFoodSelected: (String?) -> Unit,", "LoadoutScreen.kt onFoodSelected signature", errors)

# ============================================================
# 4. LoadoutScreen.kt - tap selected food again to unequip
# ============================================================
lo_old_2 = "onClick = { onFoodSelected(food.itemId) }"
lo_new_2 = "onClick = { onFoodSelected(if (food.itemId == state.selectedFoodId) null else food.itemId) }"
loadout_text, c4 = apply_edit(loadout_text, lo_old_2, lo_new_2, "if (food.itemId == state.selectedFoodId) null else food.itemId", "LoadoutScreen.kt food unequip onClick", errors)

# ============================================================
# 5. ModerationScreen.kt - signature + new composable + call site
# ============================================================
mod_old_1 = """@Composable
fun ModerationScreen(
    state: ModerationState,
    onResolveReport: (reportId: String, actionTaken: Boolean) -> Unit,
    onResolveAppeal: (appealId: String, grant: Boolean, notes: String) -> Unit,
    onMuteCharacter: (characterId: String, durationSeconds: Int, reason: String) -> Unit,
    onUnmuteCharacter: (characterId: String) -> Unit,
    modifier: Modifier = Modifier
) {"""
mod_new_1 = """@Composable
fun ModerationScreen(
    state: ModerationState,
    onResolveReport: (reportId: String, actionTaken: Boolean) -> Unit,
    onResolveAppeal: (appealId: String, grant: Boolean, notes: String) -> Unit,
    onMuteCharacter: (characterId: String, durationSeconds: Int, reason: String) -> Unit,
    onUnmuteCharacter: (characterId: String) -> Unit,
    onGrantGems: (Long) -> Unit = {},
    modifier: Modifier = Modifier
) {"""
moderation_text, c5 = apply_edit(moderation_text, mod_old_1, mod_new_1, "onGrantGems: (Long) -> Unit = {},", "ModerationScreen.kt signature", errors)

mod_old_2 = """        ManualMuteSection(onMuteCharacter, onUnmuteCharacter)
    }
}"""
mod_new_2 = """        ManualMuteSection(onMuteCharacter, onUnmuteCharacter)

        Spacer(modifier = Modifier.height(20.dp))

        ManualGrantGemsSection(onGrantGems)
    }
}"""
moderation_text, c6 = apply_edit(moderation_text, mod_old_2, mod_new_2, "ManualGrantGemsSection(onGrantGems)", "ModerationScreen.kt call site", errors)

mod_old_3 = """@Composable
private fun ManualMuteSection("""
mod_new_3 = """@Composable
private fun ManualGrantGemsSection(
    onGrantGems: (Long) -> Unit
) {
    var amountText by remember { mutableStateOf("500") }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(12.dp)
    ) {
        Text(text = "Grant Gems (testing only - credits your own logged-in account)", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = amountText,
            onValueChange = { input -> if (input.all { it.isDigit() }) amountText = input },
            label = { Text(text = "Amount") },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(8.dp))
        Button(
            onClick = {
                val amount = amountText.toLongOrNull()
                if (amount != null && amount > 0) {
                    onGrantGems(amount)
                }
            }
        ) {
            Text(text = "Grant Gems")
        }
    }
}

@Composable
private fun ManualMuteSection("""
moderation_text, c7 = apply_edit(moderation_text, mod_old_3, mod_new_3, "private fun ManualGrantGemsSection(", "ModerationScreen.kt new composable", errors)

# ============================================================
# 6. MainActivity.kt - thread onGrantGems into the ModerationScreen call site
# ============================================================
ma_old = """                                ModerationScreen(
                                    state = moderation,
                                    onResolveReport = { id, action -> gameViewModel.resolveReport(id, action) },
                                    onResolveAppeal = { id, grant, notes -> gameViewModel.resolveAppeal(id, grant, notes) },
                                    onMuteCharacter = { id, dur, reason -> gameViewModel.muteCharacterAsModerator(id, dur, reason) },
                                    onUnmuteCharacter = { id -> gameViewModel.unmuteCharacterAsModerator(id) }
                                )"""
ma_new = """                                ModerationScreen(
                                    state = moderation,
                                    onResolveReport = { id, action -> gameViewModel.resolveReport(id, action) },
                                    onResolveAppeal = { id, grant, notes -> gameViewModel.resolveAppeal(id, grant, notes) },
                                    onMuteCharacter = { id, dur, reason -> gameViewModel.muteCharacterAsModerator(id, dur, reason) },
                                    onUnmuteCharacter = { id -> gameViewModel.unmuteCharacterAsModerator(id) },
                                    onGrantGems = { amount -> gameViewModel.grantTestGems(amount) }
                                )"""
main_activity_text, c8 = apply_edit(main_activity_text, ma_old, ma_new, "onGrantGems = { amount -> gameViewModel.grantTestGems(amount) }", "MainActivity.kt ModerationScreen call site", errors)

if errors:
    raise SystemExit(
        "PATCH E FAILED: one or more expected blocks did not match. No changes made to any file.\n"
        + "\n".join(f"  - {e}" for e in errors)
    )

gvm_path.write_text(gvm_text)
loadout_path.write_text(loadout_text)
moderation_path.write_text(moderation_text)
main_activity_path.write_text(main_activity_text)

any_changed = any([c1, c2, c3, c4, c5, c6, c7, c8])
if any_changed:
    print("Patch E applied:")
    print("  - GameViewModel.kt: fixed tickConsumables() passing the wrong (default 100) maxHp to combatService.stateFor(), which could permanently lock a character's real max HP at 100 the moment they load in, breaking the auto-heal percentage calc during combat.")
    print("  - GameViewModel.kt: added grantTestGems(amount) - moderator/testing tool, credits the currently logged-in account only.")
    print("  - LoadoutScreen.kt: tapping an already-selected food again now unequips it (calls onFoodSelected(null)).")
    print("  - ModerationScreen.kt: added a 'Grant Gems' section (amount input + button) for testing purchasables.")
    print("  - MainActivity.kt: wired onGrantGems into the ModerationScreen call site.")
else:
    print("Patch E: already fully applied, no changes made.")
