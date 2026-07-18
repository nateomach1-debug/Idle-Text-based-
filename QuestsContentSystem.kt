import java.time.Duration
import java.time.Instant
import java.time.LocalDate
import java.util.UUID
import kotlin.random.Random

// =========================================================
// SHARED REWARD TYPE
// =========================================================

data class ItemReward(val itemId: String, val quantity: Int, val isTradeable: Boolean = true)

data class QuestReward(
    val currency: Long = 0,
    val xp: Map<String, Long> = emptyMap(), // skillId -> xp amount
    val items: List<ItemReward> = emptyList()
)

// =========================================================
// STANDARD QUEST OBJECTIVES
// =========================================================

sealed class QuestObjective {
    abstract val id: String
    abstract val targetAmount: Int

    data class KillMonsters(override val id: String, val monsterId: String, override val targetAmount: Int) : QuestObjective()
    data class GatherItems(override val id: String, val itemId: String, override val targetAmount: Int) : QuestObjective()
    data class ReachSkillLevel(override val id: String, val skillId: String, override val targetAmount: Int) : QuestObjective()
    data class CraftItems(override val id: String, val itemId: String, override val targetAmount: Int) : QuestObjective()
}

// =========================================================
// STANDARD QUEST DEFINITION
// =========================================================

data class QuestDefinition(
    val id: String,
    val name: String,
    val requiresNpcInteraction: Boolean,
    val prerequisiteQuestIds: List<String> = emptyList(),
    val objectives: List<QuestObjective>,
    val reward: QuestReward
)

object QuestCatalog {
    val quests = listOf(
        QuestDefinition(
            id = "goblin_trouble",
            name = "Goblin Trouble",
            requiresNpcInteraction = true,
            objectives = listOf(
                QuestObjective.KillMonsters(id = "obj-1", monsterId = "goblin_grunt", targetAmount = 5)
            ),
            reward = QuestReward(currency = 200, xp = mapOf("ATTACK" to 100))
        ),
        QuestDefinition(
            id = "smiths_request",
            name = "The Smith's Request",
            requiresNpcInteraction = true,
            prerequisiteQuestIds = listOf("goblin_trouble"),
            objectives = listOf(
                QuestObjective.GatherItems(id = "obj-1", itemId = "iron_ore", targetAmount = 10),
                QuestObjective.CraftItems(id = "obj-2", itemId = "steel_bar", targetAmount = 3)
            ),
            reward = QuestReward(
                currency = 500,
                xp = mapOf("MINING" to 150, "SMITHING" to 150),
                items = listOf(ItemReward("smiths_hammer", 1, isTradeable = false))
            )
        ),
        QuestDefinition(
            id = "silent_arrival",
            name = "Silent Arrival",
            requiresNpcInteraction = false, // auto-appears once eligible, no NPC step
            objectives = listOf(
                QuestObjective.ReachSkillLevel(id = "obj-1", skillId = "THIEVING", targetAmount = 10)
            ),
            reward = QuestReward(currency = 300)
        )
    )

    fun find(questId: String): QuestDefinition? = quests.find { it.id == questId }
}

// =========================================================
// PLAYER QUEST PROGRESS
// =========================================================

enum class QuestState { AVAILABLE, IN_PROGRESS, COMPLETED, ABANDONED }

class QuestObjectiveProgress(
    val objectiveId: String,
    var currentAmount: Int = 0
)

class PlayerQuest(
    val definition: QuestDefinition,
    var state: QuestState = QuestState.AVAILABLE,
    val objectiveProgress: MutableMap<String, QuestObjectiveProgress> =
        definition.objectives.associate { it.id to QuestObjectiveProgress(it.id) }.toMutableMap(),
    var startedAt: Instant? = null,
    var completedAt: Instant? = null
) {
    fun isFullyComplete(): Boolean = definition.objectives.all { obj ->
        (objectiveProgress[obj.id]?.currentAmount ?: 0) >= obj.targetAmount
    }
}

// =========================================================
// DAILY TASKS (separate, simpler, level-scaled, random)
// Two possible task shapes: GATHER_CRAFT (gathering/production skills)
// or KILL_MONSTER (combat skills) -- same board, same skill pool, the
// task TYPE just depends on which kind of skill got rolled.
// =========================================================

enum class DailyTaskType { GATHER_CRAFT, KILL_MONSTER }

/** What a gathering/production skill can currently produce at a given level. */
data class SkillActionOption(val skillId: String, val itemId: String, val levelRequired: Int)

object SkillActionCatalog {
    private val options = listOf(
        SkillActionOption("MINING", "iron_ore", levelRequired = 1),
        SkillActionOption("MINING", "mithril_ore", levelRequired = 25),
        SkillActionOption("WOODCUTTING", "oak_log", levelRequired = 1),
        SkillActionOption("FISHING", "trout", levelRequired = 1),
        SkillActionOption("FARMING", "wheat", levelRequired = 1),
        SkillActionOption("THIEVING", "silk_pouch", levelRequired = 1),
        SkillActionOption("SMITHING", "steel_bar", levelRequired = 20),
        SkillActionOption("COOKING", "cooked_trout", levelRequired = 1),
        SkillActionOption("CRAFTING", "leather_boots", levelRequired = 1),
        SkillActionOption("FLETCHING", "wooden_arrows", levelRequired = 1),
        SkillActionOption("ALCHEMY", "minor_healing_potion", levelRequired = 1),
        SkillActionOption("MAGIC", "enchanted_rune", levelRequired = 1)
    )

    fun availableFor(skillId: String, playerLevel: Int): List<SkillActionOption> =
        options.filter { it.skillId == skillId && it.levelRequired <= playerLevel }
}

/** What a combat skill can currently fight at a given level -- monster pool shared across all combat skills. */
data class CombatTaskOption(val monsterId: String, val levelRequired: Int)

object CombatTaskCatalog {
    private val combatSkills = setOf("ATTACK", "STRENGTH", "DEFENSE", "PRAYER", "ARCHERY")
    private val monsters = listOf(
        CombatTaskOption("goblin_grunt", levelRequired = 1),
        CombatTaskOption("wraith", levelRequired = 20)
    )

    fun isCombatSkill(skillId: String): Boolean = skillId in combatSkills

    fun availableFor(playerLevel: Int): List<CombatTaskOption> =
        monsters.filter { it.levelRequired <= playerLevel }
}

data class DailyTask(
    val id: String = UUID.randomUUID().toString(),
    val skillId: String,
    val type: DailyTaskType,
    val targetId: String, // itemId if GATHER_CRAFT, monsterId if KILL_MONSTER
    val targetAmount: Int,
    var currentAmount: Int = 0,
    val reward: QuestReward
) {
    fun isComplete(): Boolean = currentAmount >= targetAmount
}

class DailyTaskBoard(
    val date: LocalDate,
    val tasks: MutableList<DailyTask> = mutableListOf()
)

// =========================================================
// RESULT TYPE
// =========================================================

sealed class ServiceResult<out T> {
    data class Success<T>(val value: T) : ServiceResult<T>()
    data class Failure(val reason: String) : ServiceResult<Nothing>()
}

// =========================================================
// QUEST SERVICE
// =========================================================

class QuestService {
    private val playerQuests: MutableMap<String, MutableMap<String, PlayerQuest>> = mutableMapOf()
    private val completedQuestIds: MutableMap<String, MutableSet<String>> = mutableMapOf()
    private val maxActiveQuests = 3

    private fun questsFor(characterId: String) = playerQuests.getOrPut(characterId) { mutableMapOf() }
    private fun completedFor(characterId: String) = completedQuestIds.getOrPut(characterId) { mutableSetOf() }

    fun isEligible(characterId: String, questId: String): Boolean {
        val definition = QuestCatalog.find(questId) ?: return false
        val completed = completedFor(characterId)
        return definition.prerequisiteQuestIds.all { it in completed }
    }

    fun autoAvailableQuests(characterId: String): List<QuestDefinition> =
        QuestCatalog.quests.filter {
            !it.requiresNpcInteraction &&
            isEligible(characterId, it.id) &&
            it.id !in completedFor(characterId) &&
            !questsFor(characterId).containsKey(it.id)
        }

    fun startQuest(characterId: String, questId: String, now: Instant = Instant.now()): ServiceResult<PlayerQuest> {
        val definition = QuestCatalog.find(questId) ?: return ServiceResult.Failure("Quest not found.")
        if (questId in completedFor(characterId)) return ServiceResult.Failure("Quest already completed.")
        if (!isEligible(characterId, questId)) return ServiceResult.Failure("Prerequisites not met.")

        val active = questsFor(characterId).values.count { it.state == QuestState.IN_PROGRESS }
        if (active >= maxActiveQuests) return ServiceResult.Failure("Maximum of " + maxActiveQuests + " active quests reached.")

        val playerQuest = PlayerQuest(definition = definition, state = QuestState.IN_PROGRESS, startedAt = now)
        questsFor(characterId)[questId] = playerQuest
        return ServiceResult.Success(playerQuest)
    }

    fun abandonQuest(characterId: String, questId: String): ServiceResult<Unit> {
        val playerQuest = questsFor(characterId)[questId] ?: return ServiceResult.Failure("Quest not in progress.")
        if (playerQuest.state != QuestState.IN_PROGRESS) return ServiceResult.Failure("Quest is not currently in progress.")

        questsFor(characterId).remove(questId)
        return ServiceResult.Success(Unit)
    }

    fun reportProgress(characterId: String, objectiveMatcher: (QuestObjective) -> Boolean, amount: Int = 1) {
        questsFor(characterId).values
            .filter { it.state == QuestState.IN_PROGRESS }
            .forEach { playerQuest ->
                playerQuest.definition.objectives.filter(objectiveMatcher).forEach { obj ->
                    val progress = playerQuest.objectiveProgress.getValue(obj.id)
                    progress.currentAmount = (progress.currentAmount + amount).coerceAtMost(obj.targetAmount)
                }
                if (playerQuest.isFullyComplete()) {
                    playerQuest.state = QuestState.COMPLETED
                    playerQuest.completedAt = Instant.now()
                    completedFor(characterId).add(playerQuest.definition.id)
                }
            }
    }

    fun activeQuests(characterId: String): List<PlayerQuest> =
        questsFor(characterId).values.filter { it.state == QuestState.IN_PROGRESS }

    fun completedQuests(characterId: String): List<PlayerQuest> =
        questsFor(characterId).values.filter { it.state == QuestState.COMPLETED }
}

// =========================================================
// DAILY TASK SERVICE
// =========================================================

class DailyTaskService {
    private val boards: MutableMap<String, DailyTaskBoard> = mutableMapOf()
    private val maxDailyTasks = 5

    private val allSkills = listOf(
        "MINING", "WOODCUTTING", "FISHING", "FARMING", "THIEVING",
        "SMITHING", "COOKING", "CRAFTING", "FLETCHING", "ALCHEMY", "MAGIC",
        "ATTACK", "STRENGTH", "DEFENSE", "PRAYER", "ARCHERY"
    )

    fun generateBoardForToday(characterId: String, skillLevels: Map<String, Int>, today: LocalDate = LocalDate.now()): DailyTaskBoard {
        val existing = boards[characterId]
        if (existing != null && existing.date == today) return existing

        val board = DailyTaskBoard(date = today)
        val shuffledSkills = allSkills.shuffled()

        for (skillId in shuffledSkills) {
            if (board.tasks.size >= maxDailyTasks) break

            val level = skillLevels[skillId] ?: 1

            if (CombatTaskCatalog.isCombatSkill(skillId)) {
                val options = CombatTaskCatalog.availableFor(level)
                if (options.isEmpty()) continue
                val chosen = options.random()
                val targetAmount = (level * 3).coerceAtLeast(5) // level-scaled placeholder, tuning-level
                board.tasks.add(
                    DailyTask(
                        skillId = skillId,
                        type = DailyTaskType.KILL_MONSTER,
                        targetId = chosen.monsterId,
                        targetAmount = targetAmount,
                        reward = QuestReward(currency = targetAmount * 8L, xp = mapOf(skillId to (targetAmount * 12L)))
                    )
                )
            } else {
                val options = SkillActionCatalog.availableFor(skillId, level)
                if (options.isEmpty()) continue
                val chosen = options.random()
                val targetAmount = (level * 2).coerceAtLeast(5) // level-scaled placeholder, tuning-level
                board.tasks.add(
                    DailyTask(
                        skillId = skillId,
                        type = DailyTaskType.GATHER_CRAFT,
                        targetId = chosen.itemId,
                        targetAmount = targetAmount,
                        reward = QuestReward(currency = targetAmount * 5L, xp = mapOf(skillId to (targetAmount * 10L)))
                    )
                )
            }
        }

        boards[characterId] = board
        return board
    }

    fun reportGatherCraftProgress(characterId: String, itemId: String, amount: Int = 1) {
        val board = boards[characterId] ?: return
        board.tasks.filter { it.type == DailyTaskType.GATHER_CRAFT && it.targetId == itemId && !it.isComplete() }
            .forEach { it.currentAmount = (it.currentAmount + amount).coerceAtMost(it.targetAmount) }
    }

    fun reportKillProgress(characterId: String, monsterId: String, amount: Int = 1) {
        val board = boards[characterId] ?: return
        board.tasks.filter { it.type == DailyTaskType.KILL_MONSTER && it.targetId == monsterId && !it.isComplete() }
            .forEach { it.currentAmount = (it.currentAmount + amount).coerceAtMost(it.targetAmount) }
    }

    fun boardFor(characterId: String): DailyTaskBoard? = boards[characterId]
}

// =========================================================
// DEMO
// =========================================================

fun main() {
    val quests = QuestService()
    val dailies = DailyTaskService()
    val characterId = "lyra-character-id"

    println("=== Checking auto-available quests (no NPC step needed) ===")
    quests.autoAvailableQuests(characterId).forEach { println("- " + it.name) }

    println("")
    println("=== Starting 'Goblin Trouble' ===")
    printResult(quests.startQuest(characterId, "goblin_trouble"))

    println("")
    println("=== Attempting to start 'The Smith's Request' before prerequisite is done (should fail) ===")
    printResult(quests.startQuest(characterId, "smiths_request"))

    println("")
    println("=== Reporting 5 goblin kills to complete the objective ===")
    repeat(5) {
        quests.reportProgress(characterId, { obj -> obj is QuestObjective.KillMonsters && obj.monsterId == "goblin_grunt" })
    }
    println("Completed quests: " + quests.completedQuests(characterId).map { it.definition.name })

    println("")
    println("=== Now starting 'The Smith's Request' (prerequisite met) ===")
    printResult(quests.startQuest(characterId, "smiths_request"))

    println("")
    println("=== Reporting partial progress on gathering iron ore (6 of 10) ===")
    quests.reportProgress(characterId, { obj -> obj is QuestObjective.GatherItems && obj.itemId == "iron_ore" }, amount = 6)
    val smithQuest = quests.activeQuests(characterId).find { it.definition.id == "smiths_request" }
    println("Iron ore progress: " + smithQuest?.objectiveProgress?.get("obj-1")?.currentAmount + "/10")

    println("")
    println("=== Abandoning 'The Smith's Request' ===")
    printResult(quests.abandonQuest(characterId, "smiths_request"))
    println("Active quests remaining: " + quests.activeQuests(characterId).map { it.definition.name })

    println("")
    println("=== Generating today's Daily Task board (all 16 skills eligible; combat skills produce KILL tasks) ===")
    val skillLevels = mapOf(
        "MINING" to 15, "WOODCUTTING" to 5, "FISHING" to 8, "FARMING" to 3, "THIEVING" to 12,
        "SMITHING" to 22, "COOKING" to 4, "CRAFTING" to 6, "FLETCHING" to 2, "ALCHEMY" to 9, "MAGIC" to 7,
        "ATTACK" to 30, "STRENGTH" to 28, "DEFENSE" to 25, "PRAYER" to 10, "ARCHERY" to 18
    )
    val board = dailies.generateBoardForToday(characterId, skillLevels)
    board.tasks.forEach {
        val verb = if (it.type == DailyTaskType.KILL_MONSTER) "kill" else "gather/craft"
        println("- " + it.skillId + " (" + it.type + "): " + verb + " " + it.targetId + " x" + it.targetAmount + " (reward: " + it.reward.currency + " currency)")
    }
    println("Total tasks generated: " + board.tasks.size + " (should always be 5)")
    println("Unique skills used: " + board.tasks.map { it.skillId }.distinct().size + " (should equal task count -- no repeats)")

    println("")
    println("=== Reporting progress on whichever task type came up first ===")
    val firstTask = board.tasks.first()
    if (firstTask.type == DailyTaskType.KILL_MONSTER) {
        dailies.reportKillProgress(characterId, firstTask.targetId, amount = firstTask.targetAmount)
    } else {
        dailies.reportGatherCraftProgress(characterId, firstTask.targetId, amount = firstTask.targetAmount)
    }
    println(firstTask.targetId + " task complete: " + firstTask.isComplete())
}

fun <T> printResult(result: ServiceResult<T>) {
    when (result) {
        is ServiceResult.Success -> println("[OK] " + result.value)
        is ServiceResult.Failure -> println("[FAIL] " + result.reason)
    }
}
