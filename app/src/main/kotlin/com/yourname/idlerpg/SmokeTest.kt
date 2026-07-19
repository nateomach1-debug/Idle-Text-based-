package com.yourname.idlerpg

import java.time.Instant

fun main() {
    println("=== SMOKE TEST: cross-module wiring check ===")

    // ---------------- Account & Character ----------------
    println("\n--- Account & Character ---")
    val accountService = AccountService()
    val accountResult = accountService.createAccount(
        email = "smoke@test.com",
        username = "SmokeTester",
        password = "testpassword1",
        ageBracket = AgeBracket.ADULT_18_PLUS,
        region = "US"
    )
    val account = (accountResult as ServiceResult.Success).value
    println("Account created: " + account.username)

    val characterResult = accountService.createCharacter(account.id, "Smokey", "mage")
    val character = (characterResult as ServiceResult.Success).value
    println("Character created: " + character.displayName)

    val mainResult = accountService.setMainCharacter(character.id)
    println("Set as Main character: " + (mainResult is ServiceResult.Success))

    // ---------------- Skill & Progression ----------------
    println("\n--- Skill & Progression ---")
    val progressionService = ProgressionService()
    val xpResult = progressionService.grantXp(character.id, SkillType.MINING, baseXp = 5000)
    if (xpResult is ServiceResult.Success) {
        println("Mining XP granted. New level: " + xpResult.value.levelAfter)
    }

    // ---------------- Items & Equipment ----------------
    println("\n--- Items & Equipment ---")
    val inventory = Inventory()
    inventory.addItem("iron_sword_common", 1)
    inventory.addItem("iron_ore", 10)
    println("Inventory used slots: " + inventory.usedSlots())

    val equipResult = inventory.equip(
        itemId = "iron_sword_common",
        playerLevel = 15,
        playerSkillLevels = mapOf("ATTACK" to 15),
        canChangeSlot = { true }
    )
    println("Equip Iron Sword: " + (equipResult is ServiceResult.Success))
    println("Currently equipped weapon: " + inventory.equippedItemIn(EquipSlot.WEAPON))

    // ---------------- Combat ----------------
    println("\n--- Combat ---")
    val combatService = CombatService()
    combatService.stateFor(character.id, maxHp = 100)
    val zoneResult = combatService.enterZone(character.id, "goblin_camp", characterLevel = 15)
    println("Entered zone: " + (zoneResult is ServiceResult.Success))

    // ---------------- Economy & Market ----------------
    println("\n--- Economy & Market ---")
    val monitoring = EconomyMonitoringService()
    val marketService = MarketService(monitoring)
    val economyAccount = PlayerEconomyAccount(
        characterId = character.id,
        accountId = account.id,
        isMainCharacter = true,
        currencyBalance = 1000
    )
    economyAccount.addItem("iron_ore", 5)
    marketService.registerAccount(economyAccount)

    val sellResult = marketService.placeSellOrder(character.id, "iron_ore", 5, 12)
    println("Sell order placed: " + (sellResult is ServiceResult.Success))

    // ---------------- Guild ----------------
    println("\n--- Guild ---")
    val guildService = GuildService()
    val guildResult = guildService.createGuild(account.id, character.id, "Smoke Test Guild", currencyBalance = 0)
    if (guildResult is ServiceResult.Success) {
        println("Guild created: " + guildResult.value.name)
    }

    // ---------------- Quests ----------------
    println("\n--- Quests ---")
    val questService = QuestService()
    val autoQuests = questService.autoAvailableQuests(character.id)
    println("Auto-available quests: " + autoQuests.map { it.name })

    // ---------------- Monetization ----------------
    println("\n--- Monetization ---")
    val subscriptionService = SubscriptionService()
    val redeemResult = subscriptionService.redeemToken(character.id)
    println("Subscription redeemed: " + (redeemResult is ServiceResult.Success))
    println("Is subscribed: " + subscriptionService.isSubscribed(character.id))

    println("\n=== SMOKE TEST COMPLETE ===")
}
