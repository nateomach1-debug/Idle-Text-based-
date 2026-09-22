package com.yourname.idlerpg.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.yourname.idlerpg.ChatCosmetic
import com.yourname.idlerpg.ChatCosmeticCatalog
import com.yourname.idlerpg.ui.components.ChatChannelUi
import com.yourname.idlerpg.ui.components.ChatMessageUi
import com.yourname.idlerpg.ui.components.badgePreviewText
import com.yourname.idlerpg.ui.components.chatLineText

// =========================================================
// TITLES & BADGES (Settings)
// Entry card shows a live preview of what your chat line looks
// like; "Customize" opens a full-screen dialog with a Titles tab
// and a Badges tab. Titles: owned / gem shop / earn-these (with
// progress). Badges: all gem-priced, animated previews.
// =========================================================

@Composable
fun CosmeticsEntry(
    gems: Long,
    owned: Set<String>,
    equippedTitleId: String?,
    equippedBadgeId: String?,
    monsterKills: Map<String, Long>,
    skillLevels: Map<String, Int>,
    errorText: String?,
    onBuy: (String) -> Unit,
    onEquipTitle: (String?) -> Unit,
    onEquipBadge: (String?) -> Unit
) {
    var showDialog by remember { mutableStateOf(false) }
    val previewMessage = ChatMessageUi(
        id = "cosmetics-preview",
        senderCharacterId = "cosmetics-preview",
        senderName = "Your Name",
        content = "looking good!",
        channel = ChatChannelUi.GLOBAL,
        senderTitleId = equippedTitleId,
        senderBadgeId = equippedBadgeId
    )

    Column(modifier = Modifier.fillMaxWidth()) {
        Text(text = "Titles & Badges", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        Text(text = chatLineText(previewMessage), style = MaterialTheme.typography.bodyLarge)
        Spacer(modifier = Modifier.height(8.dp))
        Button(onClick = { showDialog = true }) {
            Text(text = "Customize")
        }
    }

    if (showDialog) {
        CosmeticsDialog(
            gems = gems,
            owned = owned,
            equippedTitleId = equippedTitleId,
            equippedBadgeId = equippedBadgeId,
            monsterKills = monsterKills,
            skillLevels = skillLevels,
            errorText = errorText,
            onBuy = onBuy,
            onEquipTitle = onEquipTitle,
            onEquipBadge = onEquipBadge,
            onDismiss = { showDialog = false }
        )
    }
}

@Composable
private fun CosmeticsDialog(
    gems: Long,
    owned: Set<String>,
    equippedTitleId: String?,
    equippedBadgeId: String?,
    monsterKills: Map<String, Long>,
    skillLevels: Map<String, Int>,
    errorText: String?,
    onBuy: (String) -> Unit,
    onEquipTitle: (String?) -> Unit,
    onEquipBadge: (String?) -> Unit,
    onDismiss: () -> Unit
) {
    var tab by remember { mutableStateOf(0) }

    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(usePlatformDefaultWidth = false)
    ) {
        Surface(
            modifier = Modifier.fillMaxSize().padding(12.dp),
            shape = RoundedCornerShape(16.dp),
            color = MaterialTheme.colorScheme.surface
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(text = "Titles & Badges", style = MaterialTheme.typography.titleLarge)
                    TextButton(onClick = onDismiss) {
                        Text(text = "Close")
                    }
                }
                Text(text = "Gems: " + gems, style = MaterialTheme.typography.titleSmall)
                if (errorText != null) {
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = errorText,
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.error
                    )
                }
                Spacer(modifier = Modifier.height(10.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    TabChip(label = "Titles", selected = tab == 0, onClick = { tab = 0 })
                    TabChip(label = "Badges", selected = tab == 1, onClick = { tab = 1 })
                }
                Spacer(modifier = Modifier.height(10.dp))

                if (tab == 0) {
                    TitlesList(
                        gems = gems,
                        owned = owned,
                        equippedTitleId = equippedTitleId,
                        monsterKills = monsterKills,
                        skillLevels = skillLevels,
                        onBuy = onBuy,
                        onEquipTitle = onEquipTitle
                    )
                } else {
                    BadgesList(
                        gems = gems,
                        owned = owned,
                        equippedBadgeId = equippedBadgeId,
                        onBuy = onBuy,
                        onEquipBadge = onEquipBadge
                    )
                }
            }
        }
    }
}

@Composable
private fun TabChip(label: String, selected: Boolean, onClick: () -> Unit) {
    if (selected) {
        Button(onClick = onClick) { Text(text = label) }
    } else {
        OutlinedButton(onClick = onClick) { Text(text = label) }
    }
}

@Composable
private fun SectionHeader(text: String) {
    Text(
        text = text,
        style = MaterialTheme.typography.titleSmall,
        modifier = Modifier.padding(top = 8.dp)
    )
}

@Composable
private fun CosmeticRowFrame(
    modifier: Modifier = Modifier,
    content: @Composable RowScope.() -> Unit
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(10.dp))
            .background(MaterialTheme.colorScheme.onSurface.copy(alpha = 0.07f))
            .padding(12.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        content()
    }
}

@Composable
private fun TitlesList(
    gems: Long,
    owned: Set<String>,
    equippedTitleId: String?,
    monsterKills: Map<String, Long>,
    skillLevels: Map<String, Int>,
    onBuy: (String) -> Unit,
    onEquipTitle: (String?) -> Unit
) {
    val allTitles = ChatCosmeticCatalog.allTitles
    val ownedTitles = allTitles.filter { it.id in owned }
    val shopTitles = allTitles.filter { !it.isEarned && it.id !in owned }
    val lockedEarned = allTitles.filter { it.isEarned && it.id !in owned }

    LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        item { SectionHeader("Owned (" + ownedTitles.size + ")") }
        if (ownedTitles.isEmpty()) {
            item {
                Text(
                    text = "You don't own any titles yet. Earn them in-game or buy them below.",
                    style = MaterialTheme.typography.labelMedium
                )
            }
        }
        items(ownedTitles) { title ->
            TitleRow(
                title = title,
                subtitle = if (title.isEarned) "Earned" else "Purchased",
                trailing = {
                    EquipButton(
                        equipped = title.id == equippedTitleId,
                        onEquip = { onEquipTitle(title.id) },
                        onUnequip = { onEquipTitle(null) }
                    )
                }
            )
        }

        item { SectionHeader("Gem Shop") }
        items(shopTitles) { title ->
            TitleRow(
                title = title,
                subtitle = "Costs " + title.gemCost + " Gems",
                trailing = {
                    Button(onClick = { onBuy(title.id) }, enabled = gems >= title.gemCost) {
                        Text(text = "Buy (" + title.gemCost + ")")
                    }
                }
            )
        }

        item { SectionHeader("Earn These (" + lockedEarned.size + ")") }
        items(lockedEarned) { title ->
            TitleRow(
                title = title,
                subtitle = earnRequirementText(title, monsterKills, skillLevels),
                trailing = {
                    Text(text = "Locked", style = MaterialTheme.typography.labelMedium)
                }
            )
        }
    }
}

@Composable
private fun TitleRow(
    title: ChatCosmetic,
    subtitle: String,
    trailing: @Composable () -> Unit
) {
    CosmeticRowFrame {
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = "[" + title.displayName + "]",
                color = Color(title.colorArgb),
                style = MaterialTheme.typography.titleSmall
            )
            Text(text = subtitle, style = MaterialTheme.typography.labelSmall)
        }
        Spacer(modifier = Modifier.width(8.dp))
        trailing()
    }
}

@Composable
private fun EquipButton(equipped: Boolean, onEquip: () -> Unit, onUnequip: () -> Unit) {
    if (equipped) {
        OutlinedButton(onClick = onUnequip) { Text(text = "Unequip") }
    } else {
        Button(onClick = onEquip) { Text(text = "Equip") }
    }
}

private fun earnRequirementText(
    title: ChatCosmetic,
    monsterKills: Map<String, Long>,
    skillLevels: Map<String, Int>
): String {
    val skill = title.earnedSkill
    val monsterId = title.earnedMonsterId
    return when {
        skill != null -> {
            val current = skillLevels[skill.name] ?: 0
            val label = skill.name.lowercase().replaceFirstChar { it.uppercase() }
            "Reach level " + ChatCosmeticCatalog.MASTER_SKILL_LEVEL + " in " + label + " (now " + current + ")"
        }
        monsterId != null -> {
            val kills = monsterKills[monsterId] ?: 0L
            val name = ChatCosmeticCatalog.monsterName(monsterId)
            "Defeat " + "%,d".format(ChatCosmeticCatalog.SLAYER_KILLS_REQUIRED) + " " + name +
                " (" + "%,d".format(kills) + " so far)"
        }
        else -> ""
    }
}

@Composable
private fun BadgesList(
    gems: Long,
    owned: Set<String>,
    equippedBadgeId: String?,
    onBuy: (String) -> Unit,
    onEquipBadge: (String?) -> Unit
) {
    LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        item {
            Text(
                text = "Badges change how your name looks in chat. They layer over your normal text style.",
                style = MaterialTheme.typography.labelMedium
            )
        }
        items(ChatCosmeticCatalog.badges) { badge ->
            val effect = badge.badgeEffect
            val isOwned = badge.id in owned
            CosmeticRowFrame {
                Column(modifier = Modifier.weight(1f)) {
                    if (effect != null) {
                        Text(
                            text = badgePreviewText("Your Name", effect),
                            style = MaterialTheme.typography.titleSmall
                        )
                    }
                    Text(
                        text = badge.displayName + if (isOwned) " (owned)" else " - " + badge.gemCost + " Gems",
                        style = MaterialTheme.typography.labelSmall
                    )
                }
                Spacer(modifier = Modifier.width(8.dp))
                if (isOwned) {
                    EquipButton(
                        equipped = badge.id == equippedBadgeId,
                        onEquip = { onEquipBadge(badge.id) },
                        onUnequip = { onEquipBadge(null) }
                    )
                } else {
                    Button(onClick = { onBuy(badge.id) }, enabled = gems >= badge.gemCost) {
                        Text(text = "Buy (" + badge.gemCost + ")")
                    }
                }
            }
        }
    }
}
