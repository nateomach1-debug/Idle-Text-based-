package com.yourname.idlerpg.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp

// =========================================================
// CHARACTER SELECTION + CREATION
// Selection: shown if account already has 1+ characters.
// Creation: shown if account has none, or player taps "New".
// =========================================================

data class CharacterSummaryUi(val characterId: String, val displayName: String, val avatarId: String)

@Composable
fun CharacterSelectScreen(
    characters: List<CharacterSummaryUi>,
    onCharacterSelected: (String) -> Unit,
    onCreateNew: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(24.dp)
    ) {
        Text(text = "Select a Character", style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.height(20.dp))

        characters.forEach { character ->
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 4.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(MaterialTheme.colorScheme.surface)
                    .clickable { onCharacterSelected(character.characterId) }
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(text = character.displayName, style = MaterialTheme.typography.titleMedium)
                Spacer(modifier = Modifier.width(8.dp))
                Text(text = "(" + character.avatarId + ")", style = MaterialTheme.typography.labelSmall)
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        OutlinedButton(onClick = onCreateNew, modifier = Modifier.fillMaxWidth()) {
            Text(text = "Create New Character")
        }
    }
}

@Composable
fun CharacterCreateScreen(
    errorMessage: String?,
    onCreate: (displayName: String, avatarId: String) -> Unit,
    modifier: Modifier = Modifier
) {
    var displayName by remember { mutableStateOf("") }
    var selectedAvatar by remember { mutableStateOf("knight") }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(24.dp)
    ) {
        Text(text = "Create Your Character", style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.height(20.dp))

        OutlinedTextField(
            value = displayName,
            onValueChange = { displayName = it },
            label = { Text("Character Name") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(16.dp))
        Text(text = "Choose an Avatar", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))

        val avatars = listOf("knight", "mage", "archer", "rogue", "cleric", "blacksmith")
        avatars.forEach { avatar ->
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 2.dp)
                    .clip(RoundedCornerShape(10.dp))
                    .background(
                        if (avatar == selectedAvatar) MaterialTheme.colorScheme.primary.copy(alpha = 0.2f)
                        else MaterialTheme.colorScheme.surface
                    )
                    .clickable { selectedAvatar = avatar }
                    .padding(12.dp)
            ) {
                Text(text = avatar, style = MaterialTheme.typography.bodyMedium)
            }
        }

        errorMessage?.let {
            Spacer(modifier = Modifier.height(8.dp))
            Text(text = it, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.error)
        }

        Spacer(modifier = Modifier.height(20.dp))

        Button(
            onClick = { onCreate(displayName, selectedAvatar) },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(text = "Create Character")
        }
    }
}
