#!/usr/bin/env python3
"""
patch_N1_cosmetics_core.py

Chat TITLES + BADGES - data plumbing and rendering (no settings UI yet - that is N2).
Requires cosmetics_schema.sql to have been run in Supabase first.

New files: ChatCosmeticsSystem.kt (catalog: earned Master <Skill> / Master <Monster>
Slayer titles, gem titles, gem badges), SupabaseCosmeticRepository.kt (RPC/table access),
ChatNameStyling.kt ("[Title] Name: message" rendering + the 10 badge name effects).
Edits: CombatSystem.kt (kill hook, live + offline), SupabaseChatRepository.kt (attach each
sender's equipped title/badge), ChatBanner.kt (ChatMessageUi fields, both message lines now
render through chatLineText), GameViewModel.kt (kill tally, server sync loop, earned-title
claims, purchase/equip functions).

Purely additive. Run from the repo root. Idempotent. All-or-nothing: if any anchor is
missing/ambiguous nothing is written and the script exits 1.
"""
import os
import sys

SRC = "app/src/main/kotlin/com/yourname/idlerpg"

NEW_FILES = {
    'ChatCosmeticsSystem.kt': r'''package com.yourname.idlerpg

// =========================================================
// CHAT COSMETICS CATALOG - TITLES + BADGES
// Titles show as "[Title] " before a character's name in chat.
//   - Earned titles: "Master <Skill>" (reach level 99) and
//     "Master <Monster> Slayer" (defeat 10,000 of that monster).
//     One per skill / per monster in ZoneCatalog - new monsters
//     get their Slayer title automatically.
//   - Gem titles: extra titles bought with Gems.
// Badges are name-only visual effects layered over the viewer's
// normal text effect. ALL badges cost Gems.
// Ownership and equipped state live server-side (see the
// character_owned_cosmetics / character_cosmetics tables) so other
// players see them; this file only supplies display data and the
// earn rules the client checks before claiming an earned title.
// Gem prices here MUST match the chat_cosmetics seed rows in
// cosmetics_schema.sql - the server is the source of truth for
// what a purchase actually charges.
// =========================================================

enum class CosmeticKind { TITLE, BADGE }

enum class BadgeEffect {
    RAINBOW, GILDED, INFERNO, FROSTBITE, NEON_PULSE,
    AURORA, STORMCALL, BLOOD_MOON, TOXIC, VOID
}

data class ChatCosmetic(
    val id: String,
    val kind: CosmeticKind,
    val displayName: String,
    val gemCost: Long = 0L,
    val colorArgb: Long = 0xFFFFFFFFL,
    val badgeEffect: BadgeEffect? = null,
    val earnedSkill: SkillType? = null,
    val earnedMonsterId: String? = null
) {
    val isEarned: Boolean
        get() = earnedSkill != null || earnedMonsterId != null
}

object ChatCosmeticCatalog {
    const val MASTER_SKILL_LEVEL = 99
    const val SLAYER_KILLS_REQUIRED = 10000L

    private fun skillTitleColor(skill: SkillType): Long = when (skill) {
        SkillType.MINING -> 0xFFB0B4BCL
        SkillType.WOODCUTTING -> 0xFF7FB069L
        SkillType.FISHING -> 0xFF5DA9E9L
        SkillType.FARMING -> 0xFFD4B95EL
        SkillType.THIEVING -> 0xFFA678D6L
        SkillType.SMITHING -> 0xFFE8873AL
        SkillType.COOKING -> 0xFFE0674FL
        SkillType.CRAFTING -> 0xFFB18AD8L
        SkillType.FLETCHING -> 0xFF9BCB6BL
        SkillType.ALCHEMY -> 0xFF4FD1A5L
        SkillType.MAGIC -> 0xFF6EA8FFL
        SkillType.ATTACK -> 0xFFE05252L
        SkillType.STRENGTH -> 0xFFF08A3CL
        SkillType.DEFENSE -> 0xFF6FA3D9L
        SkillType.PRAYER -> 0xFFF3E9B5L
        SkillType.ARCHERY -> 0xFF8FCB5AL
    }

    // One "Master <Skill>" title per skill, earned at level 99.
    val skillTitles: List<ChatCosmetic> = SkillType.values().map { skill ->
        ChatCosmetic(
            id = "title_master_" + skill.name.lowercase(),
            kind = CosmeticKind.TITLE,
            displayName = "Master " + skill.name.lowercase().replaceFirstChar { it.uppercase() },
            colorArgb = skillTitleColor(skill),
            earnedSkill = skill
        )
    }

    // One "Master <Monster> Slayer" title per monster currently in ZoneCatalog.
    val slayerTitles: List<ChatCosmetic> by lazy {
        ZoneCatalog.zones.flatMap { it.monsters }.map { monster ->
            ChatCosmetic(
                id = "title_slayer_" + monster.id,
                kind = CosmeticKind.TITLE,
                displayName = "Master " + monster.name + " Slayer",
                colorArgb = 0xFFFF6B4AL,
                earnedMonsterId = monster.id
            )
        }
    }

    // Titles bought with Gems.
    val gemTitles: List<ChatCosmetic> = listOf(
        ChatCosmetic(id = "title_wanderer", kind = CosmeticKind.TITLE, displayName = "Wanderer", gemCost = 100L, colorArgb = 0xFFB8C4D0L),
        ChatCosmetic(id = "title_adventurer", kind = CosmeticKind.TITLE, displayName = "Adventurer", gemCost = 100L, colorArgb = 0xFF9ED08AL),
        ChatCosmetic(id = "title_ranger", kind = CosmeticKind.TITLE, displayName = "Ranger", gemCost = 200L, colorArgb = 0xFF6FCF97L),
        ChatCosmetic(id = "title_ironclad", kind = CosmeticKind.TITLE, displayName = "Ironclad", gemCost = 250L, colorArgb = 0xFFAEB6BFL),
        ChatCosmetic(id = "title_sage", kind = CosmeticKind.TITLE, displayName = "Sage", gemCost = 250L, colorArgb = 0xFF8AB4F8L),
        ChatCosmetic(id = "title_champion", kind = CosmeticKind.TITLE, displayName = "Champion", gemCost = 300L, colorArgb = 0xFFF2C94CL),
        ChatCosmetic(id = "title_shadowwalker", kind = CosmeticKind.TITLE, displayName = "Shadowwalker", gemCost = 300L, colorArgb = 0xFFB388FFL),
        ChatCosmetic(id = "title_dreadnought", kind = CosmeticKind.TITLE, displayName = "Dreadnought", gemCost = 350L, colorArgb = 0xFFE57373L),
        ChatCosmetic(id = "title_stormbringer", kind = CosmeticKind.TITLE, displayName = "Stormbringer", gemCost = 350L, colorArgb = 0xFF64B5F6L),
        ChatCosmetic(id = "title_legend", kind = CosmeticKind.TITLE, displayName = "Legend", gemCost = 500L, colorArgb = 0xFFFFD54FL),
        ChatCosmetic(id = "title_grand_champion", kind = CosmeticKind.TITLE, displayName = "Grand Champion", gemCost = 800L, colorArgb = 0xFFFFA726L),
        ChatCosmetic(id = "title_sovereign", kind = CosmeticKind.TITLE, displayName = "Sovereign", gemCost = 1000L, colorArgb = 0xFFFF80ABL)
    )

    // Name effects. Every badge costs Gems.
    val badges: List<ChatCosmetic> = listOf(
        ChatCosmetic(id = "badge_neon_pulse", kind = CosmeticKind.BADGE, displayName = "Neon Pulse", gemCost = 200L, colorArgb = 0xFF00F5FFL, badgeEffect = BadgeEffect.NEON_PULSE),
        ChatCosmetic(id = "badge_toxic", kind = CosmeticKind.BADGE, displayName = "Toxic", gemCost = 200L, colorArgb = 0xFF7CFF3AL, badgeEffect = BadgeEffect.TOXIC),
        ChatCosmetic(id = "badge_frostbite", kind = CosmeticKind.BADGE, displayName = "Frostbite", gemCost = 300L, colorArgb = 0xFF9BE7FFL, badgeEffect = BadgeEffect.FROSTBITE),
        ChatCosmetic(id = "badge_gilded", kind = CosmeticKind.BADGE, displayName = "Gilded", gemCost = 300L, colorArgb = 0xFFFFD54FL, badgeEffect = BadgeEffect.GILDED),
        ChatCosmetic(id = "badge_inferno", kind = CosmeticKind.BADGE, displayName = "Inferno", gemCost = 350L, colorArgb = 0xFFFF7A1AL, badgeEffect = BadgeEffect.INFERNO),
        ChatCosmetic(id = "badge_blood_moon", kind = CosmeticKind.BADGE, displayName = "Blood Moon", gemCost = 350L, colorArgb = 0xFFE01B1BL, badgeEffect = BadgeEffect.BLOOD_MOON),
        ChatCosmetic(id = "badge_void", kind = CosmeticKind.BADGE, displayName = "Void", gemCost = 400L, colorArgb = 0xFFB14CFFL, badgeEffect = BadgeEffect.VOID),
        ChatCosmetic(id = "badge_aurora", kind = CosmeticKind.BADGE, displayName = "Aurora", gemCost = 450L, colorArgb = 0xFF00FFA3L, badgeEffect = BadgeEffect.AURORA),
        ChatCosmetic(id = "badge_stormcall", kind = CosmeticKind.BADGE, displayName = "Stormcall", gemCost = 450L, colorArgb = 0xFF8EA8FFL, badgeEffect = BadgeEffect.STORMCALL),
        ChatCosmetic(id = "badge_rainbow", kind = CosmeticKind.BADGE, displayName = "Rainbow", gemCost = 500L, colorArgb = 0xFFFF4D4DL, badgeEffect = BadgeEffect.RAINBOW)
    )

    val earnedTitles: List<ChatCosmetic>
        get() = skillTitles + slayerTitles

    val allTitles: List<ChatCosmetic>
        get() = earnedTitles + gemTitles

    private val byId: Map<String, ChatCosmetic> by lazy {
        (skillTitles + slayerTitles + gemTitles + badges).associateBy { it.id }
    }

    fun find(id: String): ChatCosmetic? = byId[id]

    fun monsterName(monsterId: String): String =
        ZoneCatalog.zones.flatMap { it.monsters }.find { it.id == monsterId }?.name ?: monsterId
}
''',
    'SupabaseCosmeticRepository.kt': r'''package com.yourname.idlerpg

import io.github.jan.supabase.postgrest.postgrest
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.put

// =========================================================
// SERVER ACCESS FOR CHAT COSMETICS (titles + badges) AND
// PER-MONSTER KILL COUNTS
// Ownership, equipped state and kill totals live in Supabase so
// other players see the same title/badge and so kills survive
// device changes. Gem purchases go through purchase_cosmetic,
// which spends via the server-authoritative spend_gems RPC in the
// same transaction. Every call is best-effort: failures surface as
// Result.failure / empty maps, never crashes, since local
// gameplay must never depend on any of this succeeding.
// =========================================================

@Serializable
private data class EquippedCosmeticRow(
    @SerialName("character_id") val characterId: String,
    @SerialName("equipped_title_id") val equippedTitleId: String? = null,
    @SerialName("equipped_badge_id") val equippedBadgeId: String? = null
)

data class EquippedCosmetics(val titleId: String?, val badgeId: String?)

object SupabaseCosmeticRepository {

    private val client get() = SupabaseClientProvider.client

    // Equipped title/badge for a set of characters (used to decorate chat lines).
    suspend fun fetchEquipped(characterIds: List<String>): Map<String, EquippedCosmetics> {
        if (characterIds.isEmpty()) return emptyMap()
        return try {
            client.postgrest.from("character_cosmetics")
                .select { filter { isIn("character_id", characterIds) } }
                .decodeList<EquippedCosmeticRow>()
                .associateBy({ it.characterId }, { EquippedCosmetics(it.equippedTitleId, it.equippedBadgeId) })
        } catch (e: Exception) {
            emptyMap()
        }
    }

    suspend fun myCosmetics(characterId: String): Result<List<String>> = runCatching {
        client.postgrest.rpc("my_cosmetics", buildJsonObject {
            put("p_character_id", characterId)
        }).decodeAs<List<String>>()
    }

    suspend fun monsterKills(characterId: String): Result<Map<String, Long>> = runCatching {
        client.postgrest.rpc("get_monster_kills", buildJsonObject {
            put("p_character_id", characterId)
        }).decodeAs<Map<String, Long>>()
    }

    suspend fun recordKills(characterId: String, kills: Map<String, Int>): Result<Unit> = runCatching {
        client.postgrest.rpc("record_monster_kills", buildJsonObject {
            put("p_character_id", characterId)
            put("p_kills", buildJsonObject {
                kills.forEach { (monsterId, count) -> put(monsterId, count) }
            })
        })
        Unit
    }

    suspend fun purchaseCosmetic(characterId: String, cosmeticId: String): Result<Long> = runCatching {
        client.postgrest.rpc("purchase_cosmetic", buildJsonObject {
            put("p_character_id", characterId)
            put("p_cosmetic_id", cosmeticId)
        }).decodeAs<Long>()
    }

    suspend fun claimEarnedTitle(characterId: String, cosmeticId: String): Result<Unit> = runCatching {
        client.postgrest.rpc("claim_earned_title", buildJsonObject {
            put("p_character_id", characterId)
            put("p_cosmetic_id", cosmeticId)
        })
        Unit
    }

    suspend fun setEquipped(characterId: String, titleId: String?, badgeId: String?): Result<Unit> = runCatching {
        client.postgrest.rpc("set_equipped_cosmetics", buildJsonObject {
            put("p_character_id", characterId)
            put("p_title_id", titleId)
            put("p_badge_id", badgeId)
        })
        Unit
    }
}
''',
    'ChatNameStyling.kt': r'''package com.yourname.idlerpg.ui.components

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Shadow
import androidx.compose.ui.graphics.TileMode
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.buildAnnotatedString
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.withStyle
import com.yourname.idlerpg.BadgeEffect
import com.yourname.idlerpg.ChatCosmeticCatalog
import kotlin.math.sin

// =========================================================
// CHAT NAME STYLING - titles + badge effects
// A chat line renders as:  [Title] Name: message
//   - Title: bold, single flat color (no animation).
//   - Name: optionally painted with a badge effect. The effect is a
//     SpanStyle applied to the NAME ONLY, so it layers over whatever
//     global text effect the viewer has chosen without touching the
//     app-wide Typography. Every badge effect is separate from (and
//     never reuses) the Settings text-effect modes.
// Gradients use absolute pixel offsets with a repeating tile, so the
// pattern flows across the name regardless of where it sits in the line.
// =========================================================

private const val BADGE_LOOP_MS = 3200

@Composable
fun rememberBadgePhase(): Float {
    val transition = rememberInfiniteTransition(label = "chatBadgePhase")
    val phase by transition.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = BADGE_LOOP_MS, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "chatBadgePhaseValue"
    )
    return phase
}

// A repeating horizontal gradient that scrolls as phase goes 0 -> 1. The first
// color is appended at the end so the tile loops seamlessly.
private fun flowingBrush(colors: List<Color>, phase: Float, period: Float): Brush {
    val shift = (phase % 1f) * period
    return Brush.linearGradient(
        colors = colors + colors.first(),
        start = Offset(shift, 0f),
        end = Offset(shift + period, 0f),
        tileMode = TileMode.Repeated
    )
}

fun badgeSpanStyle(effect: BadgeEffect, phase: Float): SpanStyle {
    val twoPi = (2.0 * Math.PI).toFloat()
    val pulse = (sin(phase * twoPi) + 1f) / 2f
    return when (effect) {
        BadgeEffect.RAINBOW -> SpanStyle(
            brush = flowingBrush(
                listOf(
                    Color(0xFFFF3B3B), Color(0xFFFF9F1C), Color(0xFFFFEC3D), Color(0xFF3DDC84),
                    Color(0xFF29B6F6), Color(0xFF7C4DFF), Color(0xFFE040FB)
                ),
                phase, 420f
            ),
            fontWeight = FontWeight.Bold
        )
        BadgeEffect.GILDED -> SpanStyle(
            brush = flowingBrush(
                listOf(Color(0xFFB8860B), Color(0xFFFFE27A), Color(0xFFFFF8DC), Color(0xFFFFE27A), Color(0xFFB8860B)),
                phase, 360f
            ),
            fontWeight = FontWeight.Bold
        )
        BadgeEffect.INFERNO -> {
            val flicker = (sin(phase * twoPi * 3f) + 1f) / 2f
            SpanStyle(
                brush = flowingBrush(
                    listOf(Color(0xFFFF3B00), Color(0xFFFF9A00), Color(0xFFFFE066), Color(0xFFFF9A00)),
                    (phase * 2f) % 1f, 300f
                ),
                fontWeight = FontWeight.Bold,
                shadow = Shadow(color = Color(0xFFFF3B00), blurRadius = 6f + 8f * flicker)
            )
        }
        BadgeEffect.FROSTBITE -> SpanStyle(
            brush = flowingBrush(
                listOf(Color(0xFF9BE7FF), Color(0xFFFFFFFF), Color(0xFF4FC3F7), Color(0xFFFFFFFF), Color(0xFF9BE7FF)),
                phase, 380f
            ),
            fontWeight = FontWeight.Bold,
            shadow = Shadow(color = Color(0xFF00B8D4), blurRadius = 6f)
        )
        BadgeEffect.NEON_PULSE -> SpanStyle(
            color = Color(0xFF00F5FF),
            fontWeight = FontWeight.Bold,
            shadow = Shadow(color = Color(0xFF00F5FF), blurRadius = 4f + 14f * pulse)
        )
        BadgeEffect.AURORA -> SpanStyle(
            brush = flowingBrush(
                listOf(Color(0xFF00FFA3), Color(0xFF03E1FF), Color(0xFFB388FF)),
                phase, 600f
            ),
            fontWeight = FontWeight.Bold
        )
        BadgeEffect.STORMCALL -> {
            val flash = ((phase * 2f) % 1f) < 0.08f
            if (flash) {
                SpanStyle(
                    color = Color.White,
                    fontWeight = FontWeight.Bold,
                    shadow = Shadow(color = Color(0xFFBFD7FF), blurRadius = 16f)
                )
            } else {
                SpanStyle(
                    color = Color(0xFF8EA8FF),
                    fontWeight = FontWeight.Bold,
                    shadow = Shadow(color = Color(0xFF3D5AFE), blurRadius = 4f)
                )
            }
        }
        BadgeEffect.BLOOD_MOON -> SpanStyle(
            brush = flowingBrush(
                listOf(Color(0xFF9E1B1B), Color(0xFFE01B1B), Color(0xFFFF5A5A), Color(0xFFE01B1B)),
                phase, 400f
            ),
            fontWeight = FontWeight.Bold,
            shadow = Shadow(color = Color(0xFF8B0000), blurRadius = 4f + 8f * pulse)
        )
        BadgeEffect.TOXIC -> SpanStyle(
            brush = flowingBrush(
                listOf(Color(0xFF39FF14), Color(0xFFB6FF00), Color(0xFF39FF14)),
                (phase * 2f) % 1f, 300f
            ),
            fontWeight = FontWeight.Bold,
            shadow = Shadow(color = Color(0xFF1B5E20), blurRadius = 6f)
        )
        BadgeEffect.VOID -> SpanStyle(
            brush = flowingBrush(
                listOf(Color(0xFF7B2CBF), Color(0xFFC77DFF), Color(0xFFE0AAFF), Color(0xFFC77DFF)),
                phase, 500f
            ),
            fontWeight = FontWeight.Bold,
            shadow = Shadow(color = Color(0xFF5A189A), blurRadius = 4f + 8f * pulse)
        )
    }
}

// The full rendered chat line: "[Title] Name: message". Used by both the
// collapsed banner preview and the expanded message rows.
@Composable
fun chatLineText(message: ChatMessageUi): AnnotatedString {
    val title = message.senderTitleId?.let { ChatCosmeticCatalog.find(it) }
    val effect = message.senderBadgeId?.let { ChatCosmeticCatalog.find(it) }?.badgeEffect
    val phase = if (effect != null) rememberBadgePhase() else 0f
    return buildAnnotatedString {
        if (title != null) {
            withStyle(SpanStyle(color = Color(title.colorArgb), fontWeight = FontWeight.Bold)) {
                append("[" + title.displayName + "] ")
            }
        }
        if (effect != null) {
            withStyle(badgeSpanStyle(effect, phase)) {
                append(message.senderName)
            }
        } else {
            append(message.senderName)
        }
        append(": " + message.content)
    }
}

// Just a styled name, for previews in the badge shop.
@Composable
fun badgePreviewText(name: String, effect: BadgeEffect): AnnotatedString {
    val phase = rememberBadgePhase()
    return buildAnnotatedString {
        withStyle(badgeSpanStyle(effect, phase)) {
            append(name)
        }
    }
}
''',
}

EDITS = [
    ('CombatSystem.kt',
     'kill hook property',
     '    private val states: MutableMap<String, CharacterCombatState> = mutableMapOf()',
     '    private val states: MutableMap<String, CharacterCombatState> = mutableMapOf()\n\n    // Fired once per monster kill - live combat AND offline-progress kills alike.\n    // GameViewModel uses it to keep per-monster kill counts (Slayer titles).\n    var onMonsterKilled: (String, Monster) -> Unit = { _, _ -> }'),
    ('CombatSystem.kt',
     'live kill fires hook',
     '            rollLoot(state, monster, dropRateMultiplier)\n            session.currentMonster = null',
     '            rollLoot(state, monster, dropRateMultiplier)\n            onMonsterKilled(characterId, monster)\n            session.currentMonster = null'),
    ('CombatSystem.kt',
     'offline kills fire hook',
     '            rollLoot(state, monster, dropRateMultiplier)\n        }',
     '            rollLoot(state, monster, dropRateMultiplier)\n            onMonsterKilled(characterId, monster)\n        }'),
    ('SupabaseChatRepository.kt',
     'fetch equipped cosmetics for senders',
     '            rows.sortedBy { it.sentAt }.map {\n                ChatMessageUi(',
     '            val cosmeticsBySender = SupabaseCosmeticRepository.fetchEquipped(senderIds)\n\n            rows.sortedBy { it.sentAt }.map {\n                ChatMessageUi('),
    ('SupabaseChatRepository.kt',
     'attach title/badge ids to messages',
     '                    content = it.content,\n                    channel = channel\n                )',
     '                    content = it.content,\n                    channel = channel,\n                    senderTitleId = cosmeticsBySender[it.senderCharacterId]?.titleId,\n                    senderBadgeId = cosmeticsBySender[it.senderCharacterId]?.badgeId\n                )'),
    ('ChatBanner.kt',
     'ChatMessageUi title/badge fields',
     '    val content: String,\n    val channel: ChatChannelUi\n)',
     '    val content: String,\n    val channel: ChatChannelUi,\n    val senderTitleId: String? = null,\n    val senderBadgeId: String? = null\n)'),
    ('ChatBanner.kt',
     'collapsed preview line',
     'text = msg.senderName + ": " + msg.content,',
     'text = chatLineText(msg),'),
    ('ChatBanner.kt',
     'message row line',
     'text = message.senderName + ": " + message.content,',
     'text = chatLineText(message),'),
    ('GameViewModel.kt',
     'cosmetics state, kill tally, claim loop',
     '    private val _premiumActionError = MutableStateFlow<String?>(null)\n    val premiumActionError: StateFlow<String?> = _premiumActionError.asStateFlow()',
     '    private val _premiumActionError = MutableStateFlow<String?>(null)\n    val premiumActionError: StateFlow<String?> = _premiumActionError.asStateFlow()\n\n    // =========================================================\n    // CHAT COSMETICS (titles + badges) + PER-MONSTER KILL COUNTS\n    // Ownership / equipped state / kill totals are server-side\n    // (see cosmetics_schema.sql). This block keeps a local tally of\n    // kills (live AND offline kills both fire combatService.onMonsterKilled),\n    // flushes it to the server every ~30s, loads owned/equipped state\n    // once per character, and claims earned titles (Master <Skill> at\n    // level 99, Master <Monster> Slayer at 10,000 kills) as they qualify.\n    // Everything runs in its own background loop and is best-effort -\n    // gameplay never waits on it.\n    // =========================================================\n    private val cosmeticKillTally: MutableMap<String, Int> = mutableMapOf() // key = localCharacterId + "|" + monsterId\n    private var cosmeticServerKills: Map<String, Long> = emptyMap()\n    private var cosmeticsLoadedFor: String? = null\n\n    private val _ownedCosmetics = MutableStateFlow<Set<String>>(emptySet())\n    val ownedCosmetics: StateFlow<Set<String>> = _ownedCosmetics.asStateFlow()\n\n    private val _equippedTitleId = MutableStateFlow<String?>(null)\n    val equippedTitleId: StateFlow<String?> = _equippedTitleId.asStateFlow()\n\n    private val _equippedBadgeId = MutableStateFlow<String?>(null)\n    val equippedBadgeId: StateFlow<String?> = _equippedBadgeId.asStateFlow()\n\n    private val _monsterKillTotals = MutableStateFlow<Map<String, Long>>(emptyMap())\n    val monsterKillTotals: StateFlow<Map<String, Long>> = _monsterKillTotals.asStateFlow()\n\n    private val _cosmeticSkillLevels = MutableStateFlow<Map<String, Int>>(emptyMap())\n    val cosmeticSkillLevels: StateFlow<Map<String, Int>> = _cosmeticSkillLevels.asStateFlow()\n\n    private val _cosmeticActionError = MutableStateFlow<String?>(null)\n    val cosmeticActionError: StateFlow<String?> = _cosmeticActionError.asStateFlow()\n\n    init {\n        combatService.onMonsterKilled = { killerCharacterId, monster ->\n            if (killerCharacterId == _currentCharacterId.value) {\n                synchronized(cosmeticKillTally) {\n                    val key = killerCharacterId + "|" + monster.id\n                    cosmeticKillTally[key] = (cosmeticKillTally[key] ?: 0) + 1\n                }\n            }\n        }\n        viewModelScope.launch(Dispatchers.Default) {\n            // Delay first: the constructor may still be running when this coroutine starts.\n            delay(3000L)\n            while (true) {\n                val supabaseId = _currentSupabaseCharacterId.value\n                val localId = _currentCharacterId.value\n                if (supabaseId != null && localId != null) {\n                    runCatching { cosmeticsTick(localId, supabaseId) }\n                }\n                delay(if (cosmeticsLoadedFor == supabaseId) 30_000L else 3_000L)\n            }\n        }\n    }\n\n    private suspend fun cosmeticsTick(localId: String, supabaseId: String) {\n        if (cosmeticsLoadedFor != supabaseId) {\n            val owned = SupabaseCosmeticRepository.myCosmetics(supabaseId).getOrNull() ?: return\n            val kills = SupabaseCosmeticRepository.monsterKills(supabaseId).getOrNull() ?: return\n            val equipped = SupabaseCosmeticRepository.fetchEquipped(listOf(supabaseId))[supabaseId]\n            _ownedCosmetics.value = owned.toSet()\n            _equippedTitleId.value = equipped?.titleId\n            _equippedBadgeId.value = equipped?.badgeId\n            cosmeticServerKills = kills\n            cosmeticsLoadedFor = supabaseId\n        }\n\n        val prefix = localId + "|"\n        val toSend: Map<String, Int> = synchronized(cosmeticKillTally) {\n            val mine = cosmeticKillTally.filterKeys { it.startsWith(prefix) }\n            mine.keys.forEach { cosmeticKillTally.remove(it) }\n            mine.mapKeys { it.key.removePrefix(prefix) }\n        }\n        if (toSend.isNotEmpty()) {\n            val sent = SupabaseCosmeticRepository.recordKills(supabaseId, toSend)\n            if (sent.isSuccess) {\n                val merged = cosmeticServerKills.toMutableMap()\n                toSend.forEach { (monsterId, count) -> merged[monsterId] = (merged[monsterId] ?: 0L) + count }\n                cosmeticServerKills = merged\n            } else {\n                // Put them back so the next pass retries.\n                synchronized(cosmeticKillTally) {\n                    toSend.forEach { (monsterId, count) ->\n                        val key = prefix + monsterId\n                        cosmeticKillTally[key] = (cosmeticKillTally[key] ?: 0) + count\n                    }\n                }\n            }\n        }\n\n        val pendingNow: Map<String, Int> = synchronized(cosmeticKillTally) {\n            cosmeticKillTally.filterKeys { it.startsWith(prefix) }.mapKeys { it.key.removePrefix(prefix) }\n        }\n        val totals = cosmeticServerKills.toMutableMap()\n        pendingNow.forEach { (monsterId, count) -> totals[monsterId] = (totals[monsterId] ?: 0L) + count }\n        _monsterKillTotals.value = totals\n        _cosmeticSkillLevels.value = SkillType.values().associate { it.name to skillLevel(localId, it) }\n\n        claimEarnedTitles(supabaseId)\n    }\n\n    private suspend fun claimEarnedTitles(supabaseId: String) {\n        val owned = _ownedCosmetics.value\n        val levels = _cosmeticSkillLevels.value\n        for (title in ChatCosmeticCatalog.earnedTitles) {\n            if (title.id in owned) continue\n            val skill = title.earnedSkill\n            val monsterId = title.earnedMonsterId\n            val qualifies = when {\n                skill != null -> (levels[skill.name] ?: 0) >= ChatCosmeticCatalog.MASTER_SKILL_LEVEL\n                monsterId != null -> (cosmeticServerKills[monsterId] ?: 0L) >= ChatCosmeticCatalog.SLAYER_KILLS_REQUIRED\n                else -> false\n            }\n            if (!qualifies) continue\n            val claimed = SupabaseCosmeticRepository.claimEarnedTitle(supabaseId, title.id)\n            if (claimed.isSuccess) {\n                _ownedCosmetics.value = _ownedCosmetics.value + title.id\n            }\n        }\n    }\n\n    fun purchaseCosmetic(cosmeticId: String) {\n        val supabaseId = _currentSupabaseCharacterId.value ?: return\n        val cosmetic = ChatCosmeticCatalog.find(cosmeticId) ?: return\n        if (cosmetic.isEarned) {\n            _cosmeticActionError.value = "That one is earned in-game, not bought."\n            return\n        }\n        if (cosmeticId in _ownedCosmetics.value) {\n            _cosmeticActionError.value = "You already own that."\n            return\n        }\n        viewModelScope.launch {\n            val result = SupabaseCosmeticRepository.purchaseCosmetic(supabaseId, cosmeticId)\n            result.onFailure { _cosmeticActionError.value = it.message ?: it.toString() }\n            result.onSuccess {\n                _cosmeticActionError.value = null\n                _ownedCosmetics.value = _ownedCosmetics.value + cosmeticId\n                refreshCurrency()\n            }\n        }\n    }\n\n    fun equipTitle(titleId: String?) = saveEquippedCosmetics(titleId, _equippedBadgeId.value)\n\n    fun equipBadge(badgeId: String?) = saveEquippedCosmetics(_equippedTitleId.value, badgeId)\n\n    private fun saveEquippedCosmetics(titleId: String?, badgeId: String?) {\n        val supabaseId = _currentSupabaseCharacterId.value ?: return\n        viewModelScope.launch {\n            val result = SupabaseCosmeticRepository.setEquipped(supabaseId, titleId, badgeId)\n            result.onFailure { _cosmeticActionError.value = it.message ?: it.toString() }\n            result.onSuccess {\n                _cosmeticActionError.value = null\n                _equippedTitleId.value = titleId\n                _equippedBadgeId.value = badgeId\n                refreshChatMessages()\n            }\n        }\n    }'),
]


def _find_repo_file(name):
    direct = os.path.join(SRC, name)
    if os.path.exists(direct):
        return direct
    for root, _dirs, files in os.walk("app/src/main"):
        if name in files:
            return os.path.join(root, name)
    return None


def main():
    for rfile, rtext in globals().get("REQUIRES", []):
        rpath = _find_repo_file(rfile)
        if rpath is None or rtext not in open(rpath, encoding="utf-8", newline="").read():
            print("FAIL  prerequisite missing: %s should contain %r - apply the earlier patch first." % (rfile, rtext))
            sys.exit(1)
    reads = {}
    failed = False
    plan_files = []   # (path, content, verb)
    for name, content in NEW_FILES.items():
        path = os.path.join(SRC, name)
        if os.path.exists(path):
            with open(path, encoding="utf-8", newline="") as f:
                existing = f.read()
            if existing == content:
                print("SKIP  %-34s already up to date" % name)
                continue
            plan_files.append((path, content, "UPDATE"))
        else:
            plan_files.append((path, content, "CREATE"))

    original, current = {}, {}
    for fname, label, old, new in EDITS:
        if fname not in original:
            path = _find_repo_file(fname)
            if path is None:
                print("FAIL  %s not found (run from repo root)" % fname)
                sys.exit(1)
            with open(path, encoding="utf-8", newline="") as f:
                original[fname] = f.read()
            current[fname] = original[fname]
            reads[fname] = path

    applied = skipped = 0
    for fname, label, old, new in EDITS:
        if new in original[fname]:
            print("SKIP  %-22s %s (already applied)" % (fname, label))
            skipped += 1
            continue
        n = current[fname].count(old)
        if n != 1:
            print("FAIL  %-22s %s: anchor matched %d times (expected 1)" % (fname, label, n))
            failed = True
            continue
        current[fname] = current[fname].replace(old, new, 1)
        print("OK    %-22s %s" % (fname, label))
        applied += 1
    if failed:
        print("Aborting - nothing written.")
        sys.exit(1)

    for path, content, verb in plan_files:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(content)
        print("%s %s" % (verb, os.path.basename(path)))
    for fname, path in reads.items():
        if current[fname] != original[fname]:
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(current[fname])
    print("Done. %d edit(s) applied, %d already present, %d file(s) written." % (applied, skipped, len(plan_files)))


if __name__ == "__main__":
    main()
