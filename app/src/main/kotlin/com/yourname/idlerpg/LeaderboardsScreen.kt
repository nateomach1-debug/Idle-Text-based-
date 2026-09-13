package com.yourname.idlerpg.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowDropDown
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.yourname.idlerpg.LeaderboardCategory
import com.yourname.idlerpg.LeaderboardRow

@Composable
fun LeaderboardsScreen(
    selectedCategory: LeaderboardCategory,
    rows: List<LeaderboardRow>,
    isLoading: Boolean,
    onCategorySelected: (LeaderboardCategory) -> Unit,
    modifier: Modifier = Modifier
) {
    var dropdownExpanded by remember { mutableStateOf(false) }

    Column(modifier = modifier.fillMaxSize().padding(16.dp)) {
        Text(text = "Leaderboards", style = MaterialTheme.typography.headlineSmall)
        Box(modifier = Modifier.height(12.dp))

        Box {
            OutlinedButton(
                onClick = { dropdownExpanded = true },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(text = selectedCategory.label, modifier = Modifier.weight(1f))
                Icon(imageVector = Icons.Filled.ArrowDropDown, contentDescription = null)
            }
            DropdownMenu(
                expanded = dropdownExpanded,
                onDismissRequest = { dropdownExpanded = false }
            ) {
                LeaderboardCategory.values().forEach { category ->
                    DropdownMenuItem(
                        text = { Text(category.label) },
                        onClick = {
                            onCategorySelected(category)
                            dropdownExpanded = false
                        }
                    )
                }
            }
        }

        Box(modifier = Modifier.height(16.dp))

        when {
            isLoading -> Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
            rows.isEmpty() -> Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                Text(text = "No entries yet.", style = MaterialTheme.typography.bodyMedium)
            }
            else -> LazyColumn(modifier = Modifier.fillMaxSize()) {
                items(rows) { row ->
                    val nameStyle = when (row.rank) {
                        1 -> MaterialTheme.typography.headlineSmall
                        2 -> MaterialTheme.typography.titleLarge
                        3 -> MaterialTheme.typography.titleMedium
                        else -> MaterialTheme.typography.bodyLarge
                    }
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(text = "#" + row.rank + "  " + row.name, style = nameStyle)
                        Text(text = row.valueLabel, style = MaterialTheme.typography.bodyMedium)
                    }
                    HorizontalDivider()
                }
            }
        }
    }
}
