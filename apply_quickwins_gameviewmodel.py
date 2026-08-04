#!/usr/bin/env python3
"""
Quick-wins patch, part 1: GameViewModel.kt

Adds:
- ActiveQueueInfo data class (label, secondsPerAction, startedAt)
- activeQueueInfo: StateFlow<ActiveQueueInfo?>  -- drives the live countdown on Home
- currency: StateFlow<Pair<Long, Long>>          -- (softCurrency, premiumCurrency)
- refreshActiveQueue() / refreshCurrency() helpers, wired into every
  start/stop/login/target-reached path so both flows stay accurate.

Run from repo root:
    python3 apply_quickwins_gameviewmodel.py
Then rebuild:
    ./gradlew assembleDebug --console=plain --no-daemon --no-configuration-cache
"""
import sys
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt")


def fail(msg):
    print(f"FAILED: {msg}")
    sys.exit(1)


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        fail(f"expected exactly 1 occurrence of [{label}], found {count}")
    return text.replace(old, new, 1)


def main():
    if not TARGET.exists():
        fail(f"{TARGET} not found -- run this from the repo root")

    text = TARGET.read_text()
    original = text

    if "ActiveQueueInfo" in text:
        fail("ActiveQueueInfo already present -- patch may already be applied")

    # 1. Import Instant
    text = replace_once(
        text,
        "import kotlinx.coroutines.launch\n",
        "import kotlinx.coroutines.launch\nimport java.time.Instant\n",
        "import block",
    )

    # 2. ActiveQueueInfo data class, right after OfflineSummary
    text = replace_once(
        text,
        (
            "data class OfflineSummary(\n"
            "    val awaySeconds: Long,\n"
            "    val skillActionName: String,\n"
            "    val itemName: String,\n"
            "    val quantity: Int,\n"
            "    val xpEarned: Long\n"
            ")\n\n"
            "private fun formatItemName"
        ),
        (
            "data class OfflineSummary(\n"
            "    val awaySeconds: Long,\n"
            "    val skillActionName: String,\n"
            "    val itemName: String,\n"
            "    val quantity: Int,\n"
            "    val xpEarned: Long\n"
            ")\n\n"
            "data class ActiveQueueInfo(\n"
            "    val label: String,\n"
            "    val secondsPerAction: Long,\n"
            "    val startedAt: Instant\n"
            ")\n\n"
            "private fun formatItemName"
        ),
        "OfflineSummary -> ActiveQueueInfo insertion",
    )

    # 3. New StateFlows, after _equippedItems
    text = replace_once(
        text,
        (
            "    private val _equippedItems = MutableStateFlow<Map<EquipSlot, String>>(emptyMap())\n"
            "    val equippedItems: StateFlow<Map<EquipSlot, String>> = _equippedItems.asStateFlow()\n\n"
            "    init {"
        ),
        (
            "    private val _equippedItems = MutableStateFlow<Map<EquipSlot, String>>(emptyMap())\n"
            "    val equippedItems: StateFlow<Map<EquipSlot, String>> = _equippedItems.asStateFlow()\n\n"
            "    private val _activeQueueInfo = MutableStateFlow<ActiveQueueInfo?>(null)\n"
            "    val activeQueueInfo: StateFlow<ActiveQueueInfo?> = _activeQueueInfo.asStateFlow()\n\n"
            "    private val _currency = MutableStateFlow(0L to 0L)\n"
            "    val currency: StateFlow<Pair<Long, Long>> = _currency.asStateFlow()\n\n"
            "    init {"
        ),
        "new StateFlow declarations",
    )

    # 4. refreshCurrency() call in login()
    text = replace_once(
        text,
        (
            "fun login(email: String, password: String): ServiceResult<Account> {\n"
            "    val result = accountService.login(email, password)\n"
            "    if (result is ServiceResult.Success) {\n"
            "        sessionManager.saveSession(result.value.id)\n"
            "            _currentAccountId.value = result.value.id\n"
            "    }\n"
            "    return result\n"
            "}\n"
        ),
        (
            "fun login(email: String, password: String): ServiceResult<Account> {\n"
            "    val result = accountService.login(email, password)\n"
            "    if (result is ServiceResult.Success) {\n"
            "        sessionManager.saveSession(result.value.id)\n"
            "            _currentAccountId.value = result.value.id\n"
            "            refreshCurrency()\n"
            "    }\n"
            "    return result\n"
            "}\n"
        ),
        "login()",
    )

    # 5. refreshCurrency() call in createAccount()
    text = replace_once(
        text,
        (
            "  fun createAccount(email: String, username: String, password: String): ServiceResult<Account> {\n"
            "    val result = accountService.createAccount(email, username, password, AgeBracket.ADULT_18_PLUS, \"US\")\n"
            "    if (result is ServiceResult.Success) {\n"
            "        sessionManager.saveSession(result.value.id)\n"
            "            _currentAccountId.value = result.value.id\n"
            "    }\n"
            "    return result\n"
            "  }\n"
        ),
        (
            "  fun createAccount(email: String, username: String, password: String): ServiceResult<Account> {\n"
            "    val result = accountService.createAccount(email, username, password, AgeBracket.ADULT_18_PLUS, \"US\")\n"
            "    if (result is ServiceResult.Success) {\n"
            "        sessionManager.saveSession(result.value.id)\n"
            "            _currentAccountId.value = result.value.id\n"
            "            refreshCurrency()\n"
            "    }\n"
            "    return result\n"
            "  }\n"
        ),
        "createAccount()",
    )

    # 6. refreshCurrency() call in tryAutoLogin()
    text = replace_once(
        text,
        (
            "  fun tryAutoLogin(): Account? {\n"
            "    val accountId = sessionManager.getSavedAccountId() ?: return null\n"
            "    val account = accountService.accountById(accountId) ?: return null\n"
            "    _currentAccountId.value = account.id\n"
            "    return account\n"
            "}\n"
        ),
        (
            "  fun tryAutoLogin(): Account? {\n"
            "    val accountId = sessionManager.getSavedAccountId() ?: return null\n"
            "    val account = accountService.accountById(accountId) ?: return null\n"
            "    _currentAccountId.value = account.id\n"
            "    refreshCurrency()\n"
            "    return account\n"
            "}\n"
        ),
        "tryAutoLogin()",
    )

    # 7. refreshActiveQueue() at the end of selectCharacter()
    text = replace_once(
        text,
        (
            "        offlineIdleService.recordLastSeen(characterId)\n"
            "        skillActionProgressSeconds = 0\n"
            "        craftActionProgressSeconds = 0\n"
            "        refreshSkills()\n"
            "        refreshInventory()\n"
            "    }\n\n"
            "    fun startSkillAction"
        ),
        (
            "        offlineIdleService.recordLastSeen(characterId)\n"
            "        skillActionProgressSeconds = 0\n"
            "        craftActionProgressSeconds = 0\n"
            "        refreshSkills()\n"
            "        refreshInventory()\n"
            "        refreshActiveQueue()\n"
            "    }\n\n"
            "    fun startSkillAction"
        ),
        "selectCharacter()",
    )

    # 8. refreshActiveQueue() at the end of startSkillAction()
    text = replace_once(
        text,
        (
            "    fun startSkillAction(skillType: SkillType, itemId: String) {\n"
            "        val characterId = _currentCharacterId.value ?: return\n"
            "        val action = ActionCatalog.find(skillType, itemId) ?: return\n"
            "        offlineIdleService.stopQueue(characterId)\n"
            "        offlineIdleService.startSkillingQueue(characterId, skillType.name, itemId, action.secondsPerAction)\n"
            "        offlineIdleService.recordLastSeen(characterId)\n"
            "        skillActionProgressSeconds = 0\n"
            "    }\n"
        ),
        (
            "    fun startSkillAction(skillType: SkillType, itemId: String) {\n"
            "        val characterId = _currentCharacterId.value ?: return\n"
            "        val action = ActionCatalog.find(skillType, itemId) ?: return\n"
            "        offlineIdleService.stopQueue(characterId)\n"
            "        offlineIdleService.startSkillingQueue(characterId, skillType.name, itemId, action.secondsPerAction)\n"
            "        offlineIdleService.recordLastSeen(characterId)\n"
            "        skillActionProgressSeconds = 0\n"
            "        refreshActiveQueue()\n"
            "    }\n"
        ),
        "startSkillAction()",
    )

    # 9. refreshActiveQueue() at the end of stopSkillAction()
    text = replace_once(
        text,
        (
            "    fun stopSkillAction() {\n"
            "        val characterId = _currentCharacterId.value ?: return\n"
            "        offlineIdleService.stopQueue(characterId)\n"
            "        skillActionProgressSeconds = 0\n"
            "    }\n"
        ),
        (
            "    fun stopSkillAction() {\n"
            "        val characterId = _currentCharacterId.value ?: return\n"
            "        offlineIdleService.stopQueue(characterId)\n"
            "        skillActionProgressSeconds = 0\n"
            "        refreshActiveQueue()\n"
            "    }\n"
        ),
        "stopSkillAction()",
    )

    # 10. refreshActiveQueue() at the end of startCraftingAction()
    text = replace_once(
        text,
        (
            "        offlineIdleService.recordLastSeen(characterId)\n"
            "        craftActionProgressSeconds = 0\n"
            "    }\n\n"
            "    fun stopCraftingAction"
        ),
        (
            "        offlineIdleService.recordLastSeen(characterId)\n"
            "        craftActionProgressSeconds = 0\n"
            "        refreshActiveQueue()\n"
            "    }\n\n"
            "    fun stopCraftingAction"
        ),
        "startCraftingAction()",
    )

    # 11. refreshActiveQueue() at the end of stopCraftingAction()
    text = replace_once(
        text,
        (
            "    fun stopCraftingAction() {\n"
            "        val characterId = _currentCharacterId.value ?: return\n"
            "        offlineIdleService.stopQueue(characterId)\n"
            "        craftActionProgressSeconds = 0\n"
            "    }\n"
        ),
        (
            "    fun stopCraftingAction() {\n"
            "        val characterId = _currentCharacterId.value ?: return\n"
            "        offlineIdleService.stopQueue(characterId)\n"
            "        craftActionProgressSeconds = 0\n"
            "        refreshActiveQueue()\n"
            "    }\n"
        ),
        "stopCraftingAction()",
    )

    # 12. refreshActiveQueue() when a crafting target quantity is reached (tickCrafting)
    text = replace_once(
        text,
        (
            "        if (queue.isTargetReached()) {\n"
            "            offlineIdleService.stopQueue(characterId)\n"
            "        }\n"
            "    }\n"
        ),
        (
            "        if (queue.isTargetReached()) {\n"
            "            offlineIdleService.stopQueue(characterId)\n"
            "            refreshActiveQueue()\n"
            "        }\n"
            "    }\n"
        ),
        "tickCrafting() target-reached branch",
    )

    # 13. New helper functions, before the closing brace of the class
    #     (right after refreshInventory())
    text = replace_once(
        text,
        (
            "    fun refreshInventory() {\n"
            "        val characterId = _currentCharacterId.value ?: return\n"
            "        val inv = inventoryService.inventoryFor(characterId)\n"
            "        _inventoryItems.value = inv.allItems()\n"
            "        _equippedItems.value = inv.allEquipped()\n"
            "    }\n"
            "}\n"
        ),
        (
            "    fun refreshInventory() {\n"
            "        val characterId = _currentCharacterId.value ?: return\n"
            "        val inv = inventoryService.inventoryFor(characterId)\n"
            "        _inventoryItems.value = inv.allItems()\n"
            "        _equippedItems.value = inv.allEquipped()\n"
            "    }\n\n"
            "    fun refreshActiveQueue() {\n"
            "        val characterId = _currentCharacterId.value\n"
            "        val queue = characterId?.let { offlineIdleService.activeQueueFor(it) }\n"
            "        _activeQueueInfo.value = when (queue) {\n"
            "            is ActiveQueue.SkillingQueue -> {\n"
            "                val skillType = SkillType.valueOf(queue.skillId)\n"
            "                val action = ActionCatalog.find(skillType, queue.itemId)\n"
            "                ActiveQueueInfo(\n"
            "                    label = action?.displayName ?: formatItemName(queue.itemId),\n"
            "                    secondsPerAction = queue.secondsPerAction,\n"
            "                    startedAt = queue.startedAt\n"
            "                )\n"
            "            }\n"
            "            is ActiveQueue.CraftingQueue -> ActiveQueueInfo(\n"
            "                label = \"Crafting \" + formatItemName(queue.itemId),\n"
            "                secondsPerAction = queue.secondsPerAction,\n"
            "                startedAt = queue.startedAt\n"
            "            )\n"
            "            else -> null\n"
            "        }\n"
            "    }\n\n"
            "    fun refreshCurrency() {\n"
            "        val accountId = _currentAccountId.value ?: return\n"
            "        val account = accountService.accountById(accountId) ?: return\n"
            "        _currency.value = account.softCurrency to account.premiumCurrency\n"
            "    }\n"
            "}\n"
        ),
        "closing brace -> refreshActiveQueue/refreshCurrency insertion",
    )

    if text == original:
        fail("no changes were made -- aborting")

    TARGET.write_text(text)
    print(f"OK: patched {TARGET}")
    print("Run: git diff", TARGET, "to verify before rebuilding.")


if __name__ == "__main__":
    main()
