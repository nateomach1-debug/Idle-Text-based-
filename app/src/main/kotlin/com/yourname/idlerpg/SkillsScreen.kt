package com.yourname.idlerpg.ui.screens

import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.GridItemSpan
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.GridView
import androidx.compose.material.icons.filled.ViewList
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp

// =========================================================
// SKILLS LIST SCREEN
// Grouped in gathering-to-production pairs, combat skills last.
// Toggle between grid (compact) and list (more detail per row).
// The chosen view mode PERSISTS across app sessions via
// SharedPreferences -- a deliberate player preference, not a
// temporary UI state.
// =========================================================

enum class SkillsViewMode { LIST, GRID }

private const val PREFS_NAME = "idlerpg_prefs"
private const val KEY_SKILLS_VIEW_MODE = "skills_view_mode"

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
    modifier: Modifier = Modifier
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
            Text(text = "Skills", style = MaterialTheme.typography.headlineMedium)
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
            SkillsViewMode.LIST -> SkillsListView(sections, onSkillSelected)
            SkillsViewMode.GRID -> SkillsGridView(sections, onSkillSelected)
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
private fun SkillsListView(sections: List<SkillGroupSection>, onSkillSelected: (String) -> Unit) {
    LazyColumn(verticalArrangement = Arrangement.spacedBy(4.dp)) {
        sections.forEach { section ->
            item { SectionHeader(section.title) }
            items(section.skills) { skill ->
                SkillListRow(skill, onClick = { onSkillSelected(skill.skillId) })
            }
        }
    }
}

@Composable
private fun SkillsGridView(sections: List<SkillGroupSection>, onSkillSelected: (String) -> Unit) {
    LazyVerticalGrid(
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
            Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                Text(text = skill.displayName, style = MaterialTheme.typography.titleMedium)
                Text(text = "Lv. " + skill.level, style = MaterialTheme.typography.titleMedium)
            }
            Spacer(modifier = Modifier.height(6.dp))
            ThinProgressBar(progressFraction)
        }
    }
}

@Composable
private fun SkillGridTile(skill: SkillSummary, onClick: () -> Unit) {
    Column(
        modifier = Modifier
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .clickable { onClick() }
            .padding(12.dp)
            .fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = skill.displayName, style = MaterialTheme.typography.labelSmall)
        Spacer(modifier = Modifier.height(4.dp))
        Text(text = "Lv. " + skill.level, style = MaterialTheme.typography.titleMedium)
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
