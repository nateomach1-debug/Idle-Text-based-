import java.time.Duration
import java.time.Instant
import java.util.UUID
import kotlin.random.Random

// =========================================================
// SERVER-WIDE RANDOM SKILL EVENTS
// =========================================================

data class ActiveSkillEvent(
    val id: String = UUID.randomUUID().toString(),
    val skillId: String,
    val bonusPercent: Double,
    val triggeredByCharacterId: String,
    val triggerBonusPercent: Double,
    val startedAt: Instant,
    val expiresAt: Instant
) {
    fun isActive(now: Instant = Instant.now()): Boolean = now.isBefore(expiresAt)

    fun bonusFor(characterId: String): Double =
        if (characterId == triggeredByCharacterId) bonusPercent + triggerBonusPercent else bonusPercent
}

class SkillEventService {
    private val activeEventsBySkill: MutableMap<String, ActiveSkillEvent> = mutableMapOf()
    private val onlineActiveInSkill: MutableMap<String, MutableSet<String>> = mutableMapOf()

    private val triggerChancePercent = 1.0
    private val minDurationMinutes = 5L
    private val maxDurationMinutes = 15L
    private val baseBonusPercent = 10.0
    private val triggerBonusPercent = 15.0

    fun setActiveInSkill(characterId: String, skillId: String, active: Boolean) {
        val set = onlineActiveInSkill.getOrPut(skillId) { mutableSetOf() }
        if (active) set.add(characterId) else set.remove(characterId)
    }

    fun rollForEventTrigger(characterId: String, skillId: String, now: Instant = Instant.now()): ActiveSkillEvent? {
        val existing = activeEventsBySkill[skillId]
        if (existing != null && existing.isActive(now)) return null

        val roll = Random.nextDouble(0.0, 100.0)
        if (roll >= triggerChancePercent) return null

        val durationMinutes = Random.nextLong(minDurationMinutes, maxDurationMinutes + 1)
        val event = ActiveSkillEvent(
            skillId = skillId,
            bonusPercent = baseBonusPercent,
            triggeredByCharacterId = characterId,
            triggerBonusPercent = triggerBonusPercent,
            startedAt = now,
            expiresAt = now.plus(Duration.ofMinutes(durationMinutes))
        )
        activeEventsBySkill[skillId] = event
        return event
    }

    fun currentBonusFor(characterId: String, skillId: String, now: Instant = Instant.now()): Double {
        val event = activeEventsBySkill[skillId] ?: return 0.0
        if (!event.isActive(now)) return 0.0
        val isOnlineAndActive = onlineActiveInSkill[skillId]?.contains(characterId) == true
        if (!isOnlineAndActive) return 0.0
        return event.bonusFor(characterId)
    }

    fun activeEventFor(skillId: String, now: Instant = Instant.now()): ActiveSkillEvent? {
        val event = activeEventsBySkill[skillId] ?: return null
        return if (event.isActive(now)) event else null
    }
}

// =========================================================
// WORLD EVENTS
// =========================================================

enum class WorldEventTriggerType { SCHEDULED, SURPRISE }
enum class WorldEventStatus { UPCOMING, ACTIVE, COMPLETED, EXPIRED }

data class WorldEventDefinition(
    val id: String,
    val name: String,
    val triggerType: WorldEventTriggerType,
    val scheduledStartAt: Instant?,
    val durationMinutes: Long,
    val baseRewardPerParticipant: Long,
    val effortRewardPerUnit: Long
)

class WorldEventInstance(
    val definition: WorldEventDefinition,
    val startedAt: Instant,
    var status: WorldEventStatus = WorldEventStatus.ACTIVE,
    val participants: MutableSet<String> = mutableSetOf(),
    val contributionByParticipant: MutableMap<String, Long> = mutableMapOf()
) {
    val expiresAt: Instant get() = startedAt.plus(Duration.ofMinutes(definition.durationMinutes))
    fun isActive(now: Instant = Instant.now()): Boolean = status == WorldEventStatus.ACTIVE && now.isBefore(expiresAt)
    fun totalContribution(): Long = contributionByParticipant.values.sum()
}

class WorldEventService {
    private val activeInstances: MutableMap<String, WorldEventInstance> = mutableMapOf()

    fun startEvent(definition: WorldEventDefinition, now: Instant = Instant.now()): ServiceResult<WorldEventInstance> {
        val existing = activeInstances[definition.id]
        if (existing != null && existing.isActive(now)) {
            return ServiceResult.Failure("Event '" + definition.name + "' is already active.")
        }

        val instance = WorldEventInstance(definition = definition, startedAt = now)
        activeInstances[definition.id] = instance
        return ServiceResult.Success(instance)
    }

    fun optIn(eventDefinitionId: String, characterId: String, now: Instant = Instant.now()): ServiceResult<Unit> {
        val instance = activeInstances[eventDefinitionId] ?: return ServiceResult.Failure("Event is not currently active.")
        if (!instance.isActive(now)) return ServiceResult.Failure("Event is not currently active.")

        instance.participants.add(characterId)
        instance.contributionByParticipant.putIfAbsent(characterId, 0)
        return ServiceResult.Success(Unit)
    }

    fun reportContribution(eventDefinitionId: String, characterId: String, amount: Long): ServiceResult<Unit> {
        val instance = activeInstances[eventDefinitionId] ?: return ServiceResult.Failure("Event is not currently active.")
        if (characterId !in instance.participants) return ServiceResult.Failure("Character has not opted in to this event.")

        instance.contributionByParticipant[characterId] = (instance.contributionByParticipant[characterId] ?: 0) + amount
        return ServiceResult.Success(Unit)
    }

    fun resolveEvent(eventDefinitionId: String, now: Instant = Instant.now()): ServiceResult<Map<String, Long>> {
        val instance = activeInstances[eventDefinitionId] ?: return ServiceResult.Failure("Event not found.")
        if (now.isBefore(instance.expiresAt)) return ServiceResult.Failure("Event has not ended yet.")
        if (instance.status != WorldEventStatus.ACTIVE) return ServiceResult.Failure("Event already resolved.")

        instance.status = WorldEventStatus.COMPLETED

        val rewards = instance.participants.associateWith { characterId ->
            val contribution = instance.contributionByParticipant[characterId] ?: 0
            instance.definition.baseRewardPerParticipant + (contribution * instance.definition.effortRewardPerUnit)
        }

        return ServiceResult.Success(rewards)
    }

    fun activeInstance(eventDefinitionId: String, now: Instant = Instant.now()): WorldEventInstance? {
        val instance = activeInstances[eventDefinitionId] ?: return null
        return if (instance.isActive(now)) instance else null
    }
}

// =========================================================
// SEASONAL CONTENT
// =========================================================

data class SeasonDefinition(
    val id: String,
    val name: String,
    val startsAt: Instant,
    val endsAt: Instant,
    val trackedStatIds: List<String>,
    val cosmeticRewardId: String
)

class SeasonParticipation(
    val characterId: String,
    val optedInAt: Instant,
    val statTotals: MutableMap<String, Long> = mutableMapOf()
)

class SeasonService {
    private val seasons: MutableMap<String, SeasonDefinition> = mutableMapOf()
    private val participation: MutableMap<String, MutableMap<String, SeasonParticipation>> = mutableMapOf()

    fun createSeason(definition: SeasonDefinition) {
        seasons[definition.id] = definition
        participation[definition.id] = mutableMapOf()
    }

    fun optIn(seasonId: String, characterId: String, now: Instant = Instant.now()): ServiceResult<Unit> {
        val season = seasons[seasonId] ?: return ServiceResult.Failure("Season not found.")
        if (now.isAfter(season.endsAt)) return ServiceResult.Failure("Season has already ended.")

        val seasonParticipants = participation.getOrPut(seasonId) { mutableMapOf() }
        if (seasonParticipants.containsKey(characterId)) return ServiceResult.Failure("Already opted in.")

        seasonParticipants[characterId] = SeasonParticipation(characterId, now)
        return ServiceResult.Success(Unit)
    }

    fun recordStat(seasonId: String, characterId: String, statId: String, amount: Long): ServiceResult<Unit> {
        val season = seasons[seasonId] ?: return ServiceResult.Failure("Season not found.")
        if (statId !in season.trackedStatIds) return ServiceResult.Failure("Stat '" + statId + "' is not tracked this season.")

        val seasonParticipant = participation[seasonId]?.get(characterId)
            ?: return ServiceResult.Failure("Character has not opted in to this season.")

        seasonParticipant.statTotals[statId] = (seasonParticipant.statTotals[statId] ?: 0) + amount
        return ServiceResult.Success(Unit)
    }

    fun leaderboard(seasonId: String, statId: String): List<Pair<String, Long>> {
        val seasonParticipants = participation[seasonId] ?: return emptyList()
        return seasonParticipants.values
            .map { it.characterId to (it.statTotals[statId] ?: 0) }
            .sortedByDescending { it.second }
    }

    fun isOptedIn(seasonId: String, characterId: String): Boolean =
        participation[seasonId]?.containsKey(characterId) == true

    fun cosmeticEligible(seasonId: String, characterId: String): Boolean = isOptedIn(seasonId, characterId)
}

// =========================================================
// PATCH / LIVE-OPS TOOLING
// =========================================================

enum class PatchStatus { PUBLISHED, ROLLED_BACK }

data class PatchNote(
    val id: String = UUID.randomUUID().toString(),
    val version: String,
    val title: String,
    val changes: List<String>,
    val rollbackInstructions: String,
    val publishedAt: Instant = Instant.now(),
    var status: PatchStatus = PatchStatus.PUBLISHED
)

class PatchNoteService {
    private val patches: MutableList<PatchNote> = mutableListOf()

    fun publish(version: String, title: String, changes: List<String>, rollbackInstructions: String): PatchNote {
        val note = PatchNote(version = version, title = title, changes = changes, rollbackInstructions = rollbackInstructions)
        patches.add(note)
        return note
    }

    fun rollback(patchId: String): ServiceResult<PatchNote> {
        val patch = patches.find { it.id == patchId } ?: return ServiceResult.Failure("Patch not found.")
        if (patch.status == PatchStatus.ROLLED_BACK) return ServiceResult.Failure("Patch already rolled back.")

        patch.status = PatchStatus.ROLLED_BACK
        return ServiceResult.Success(patch)
    }

    fun publicRoadmap(): List<PatchNote> = patches.filter { it.status == PatchStatus.PUBLISHED }
    fun fullHistory(): List<PatchNote> = patches.toList()
}
