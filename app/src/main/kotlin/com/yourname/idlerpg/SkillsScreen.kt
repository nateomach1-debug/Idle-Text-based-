package com.yourname.idlerpg.ui.screens

import com.yourname.idlerpg.ui.theme.overrideColor

import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.GridItemSpan
import androidx.compose.foundation.lazy.grid.LazyGridState
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.grid.rememberLazyGridState
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyListState
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.GridView
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.ViewList
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp

enum class SkillsViewMode { LIST, GRID }

private const val PREFS_NAME = "idlerpg_prefs"
private const val KEY_SKILLS_VIEW_MODE = "skills_view_mode"

private val SKILL_DESCRIPTIONS: Map<String, String> = mapOf(
    "MINING" to "Mine ore from rocks. Higher levels unlock better ore and mine faster.",
    "WOODCUTTING" to "Chop trees for logs. Higher levels unlock better trees and chop faster.",
    "FISHING" to "Catch fish at fishing spots. Higher levels unlock better fish and catch faster.",
    "FARMING" to "Harvest crops from farm plots. Higher levels unlock better crops and harvest faster.",
    "THIEVING" to "Pickpocket and steal for loot and coin. Higher levels unlock riskier, more rewarding targets.",
    "SMITHING" to "Smelt ore into bars and forge them into weapons and armor.",
    "COOKING" to "Cook raw food into meals you can eat to heal during combat.",
    "CRAFTING" to "Craft leather, cloth, and jewelry into wearable gear.",
    "FLETCHING" to "Craft bows and arrows for use with the Archery combat style.",
    "ALCHEMY" to "Brew potions that grant temporary combat and skilling boosts.",
    "MAGIC" to "Train your magic combat style, and unlock utility spells like teleportation.",
    "ATTACK" to "Trains your melee hit chance. Higher levels land more hits with melee weapons.",
    "STRENGTH" to "Trains your melee hit damage. Higher levels deal more damage per hit with melee weapons.",
    "DEFENSE" to "Reduces the damage you take from monsters. Higher levels reduce incoming damage further.",
    "PRAYER" to "Activate prayers for combat bonuses like extra damage reduction.",
    "ARCHERY" to "Trains your ranged hit chance and damage when fighting with a bow."
)

@Composable
private fun SkillInfoButton(skillId: String) {
    var showDialog by remember { mutableStateOf(false) }
    IconButton(onClick = { showDialog = true }, modifier = Modifier.size(28.dp)) {
        Icon(
            imageVector = Icons.Filled.Info,
            contentDescription = "What does this skill do?",
            tint = overrideColor(MaterialTheme.colorScheme.onSurfaceVariant)
        )
    }
    if (showDialog) {
        AlertDialog(
            onDismissRequest = { showDialog = false },
            confirmButton = {
                TextButton(onClick = { showDialog = false }) { Text("Got it") }
            },
            title = { Text(skillId.lowercase().replaceFirstChar { it.uppercase() }) },
            text = { Text(SKILL_DESCRIPTIONS[skillId] ?: "No description available.") }
        )
    }
}

private fun loadSavedViewMode(context: Context): SkillsViewMode {
    val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    val saved = prefs.getString(KEY_SKILLS_VIEW_MODE, SkillsViewMode.LIST.name)
    return runCatching { SkillsViewMode.valueOf(saved ?: SkillsViewMode.LIST.name) }
        .getOrDefault(SkillsViewMode.LIST)
}

private fun saveViewMode(context: Context, mode: SkillsViewMode) {
    val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    prefs.edit().putString(KEY_SKILLS_VIEW_MODE, mode.name).apply()
}

data class SkillSummary(
    val skillId: String,
    val displayName: String,
    val level: Int,
    val currentXp: Long,
    val xpToNextLevel: Long
)

data class SkillGroupSection(
    val title: String,
    val skills: List<SkillSummary>
)

fun buildSkillGroupSections(allSkills: Map<String, SkillSummary>): List<SkillGroupSection> {
    fun skill(id: String): SkillSummary? = allSkills[id]

    val pairedSections = listOf(
        "Mining & Smithing" to listOf("MINING", "SMITHING"),
        "Fishing & Cooking" to listOf("FISHING", "COOKING"),
        "Woodcutting & Fletching" to listOf("WOODCUTTING", "FLETCHING"),
        "Farming & Alchemy" to listOf("FARMING", "ALCHEMY"),
        "Thieving & Crafting" to listOf("THIEVING", "CRAFTING")
    ).map { (title, ids) ->
        SkillGroupSection(title, ids.mapNotNull { skill(it) })
    }

    val combatSection = SkillGroupSection(
        title = "Combat",
        skills = listOf("ATTACK", "STRENGTH", "DEFENSE", "ARCHERY", "PRAYER", "MAGIC").mapNotNull { skill(it) }
    )

    return pairedSections + combatSection
}

@Composable
fun SkillsScreen(
    allSkills: Map<String, SkillSummary>,
    onSkillSelected: (String) -> Unit,
    modifier: Modifier = Modifier,
    listState: LazyListState = rememberLazyListState(),
    gridState: LazyGridState = rememberLazyGridState()
) {
    val context = LocalContext.current
    var viewMode by remember { mutableStateOf(loadSavedViewMode(context)) }
    val sections = remember(allSkills) { buildSkillGroupSections(allSkills) }

    Column(modifier = modifier.fillMaxSize().padding(20.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(text = "Skills", style = MaterialTheme.typography.headlineMedium)
                val totalLevel = remember(allSkills) { allSkills.values.sumOf { it.level } }
                Text(
                    text = "Total level: " + totalLevel,
                    style = MaterialTheme.typography.labelMedium,
                    color = overrideColor(MaterialTheme.colorScheme.onSurfaceVariant)
                )
            }
            ViewModeToggle(
                current = viewMode,
                onChange = {
                    viewMode = it
                    saveViewMode(context, it)
                }
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        when (viewMode) {
            SkillsViewMode.LIST -> SkillsListView(sections, onSkillSelected, listState)
            SkillsViewMode.GRID -> SkillsGridView(sections, onSkillSelected, gridState)
        }
    }
}

@Composable
private fun ViewModeToggle(current: SkillsViewMode, onChange: (SkillsViewMode) -> Unit) {
    Row {
        IconButton(onClick = { onChange(SkillsViewMode.LIST) }) {
            Icon(
                imageVector = Icons.Filled.ViewList,
                contentDescription = "List view",
                tint = if (current == SkillsViewMode.LIST) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface
            )
        }
        IconButton(onClick = { onChange(SkillsViewMode.GRID) }) {
            Icon(
                imageVector = Icons.Filled.GridView,
                contentDescription = "Grid view",
                tint = if (current == SkillsViewMode.GRID) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface
            )
        }
    }
}

@Composable
private fun SkillsListView(
    sections: List<SkillGroupSection>,
    onSkillSelected: (String) -> Unit,
    listState: LazyListState
) {
    LazyColumn(state = listState, verticalArrangement = Arrangement.spacedBy(4.dp)) {
        sections.forEach { section ->
            item { SectionHeader(section.title) }
            items(section.skills) { skill ->
                SkillListRow(skill, onClick = { onSkillSelected(skill.skillId) })
            }
        }
    }
}

@Composable
private fun SkillsGridView(
    sections: List<SkillGroupSection>,
    onSkillSelected: (String) -> Unit,
    gridState: LazyGridState
) {
    LazyVerticalGrid(
        state = gridState,
        columns = GridCells.Fixed(3),
        verticalArrangement = Arrangement.spacedBy(10.dp),
        horizontalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        sections.forEach { section ->
            item(span = { GridItemSpan(maxLineSpan) }) { SectionHeader(section.title) }
            items(section.skills) { skill ->
                SkillGridTile(skill, onClick = { onSkillSelected(skill.skillId) })
            }
        }
    }
}

@Composable
private fun SectionHeader(title: String) {
    Text(
        text = title,
        style = MaterialTheme.typography.labelSmall,
        modifier = Modifier.padding(top = 12.dp, bottom = 4.dp)
    )
}

@Composable
private fun SkillListRow(skill: SkillSummary, onClick: () -> Unit) {
    val progressFraction = skillProgressFraction(skill)

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .clickable { onClick() }
            .padding(14.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(text = skill.displayName, style = MaterialTheme.typography.titleMedium)
                    SkillInfoButton(skillId = skill.skillId)
                }
                Text(text = "Lv. " + skill.level, style = MaterialTheme.typography.titleMedium)
            }
            Spacer(modifier = Modifier.height(6.dp))
            ThinProgressBar(progressFraction)
            Spacer(modifier = Modifier.height(2.dp))
            Text(
                text = formatXpProgress(skill),
                style = MaterialTheme.typography.labelSmall,
                color = overrideColor(MaterialTheme.colorScheme.onSurfaceVariant),
                modifier = Modifier.fillMaxWidth(),
                textAlign = androidx.compose.ui.text.style.TextAlign.End
            )
        }
    }
}

@Composable
private fun SkillGridTile(skill: SkillSummary, onClick: () -> Unit) {
    val progressFraction = skillProgressFraction(skill)
    Column(
        modifier = Modifier
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .clickable { onClick() }
            .padding(12.dp)
            .fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(text = skill.displayName, style = MaterialTheme.typography.labelSmall)
            SkillInfoButton(skillId = skill.skillId)
        }
        Spacer(modifier = Modifier.height(4.dp))
        Text(text = "Lv. " + skill.level, style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(4.dp))
        ThinProgressBar(progressFraction)
        Spacer(modifier = Modifier.height(2.dp))
        Text(
            text = formatXpProgress(skill),
            style = MaterialTheme.typography.labelSmall,
            color = overrideColor(MaterialTheme.colorScheme.onSurfaceVariant)
        )
    }
}

@Composable
private fun ThinProgressBar(fraction: Float) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(6.dp)
            .clip(RoundedCornerShape(3.dp))
            .background(MaterialTheme.colorScheme.background)
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth(fraction)
                .fillMaxHeight()
                .clip(RoundedCornerShape(3.dp))
                .background(MaterialTheme.colorScheme.primary)
        )
    }
}

private fun skillProgressFraction(skill: SkillSummary): Float {
    val total = skill.currentXp + skill.xpToNextLevel
    if (total <= 0) return 0f
    return (skill.currentXp.toFloat() / total.toFloat()).coerceIn(0f, 1f)
}

private fun formatXpProgress(skill: SkillSummary): String {
    val total = skill.currentXp + skill.xpToNextLevel
    return "%,d / %,d XP".format(skill.currentXp, total)
}
