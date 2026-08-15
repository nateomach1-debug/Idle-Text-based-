path = "app/src/main/kotlin/com/yourname/idlerpg/GuildCreateJoinScreen.kt"

content = '''package com.yourname.idlerpg

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun GuildCreateJoinScreen(
    browsableGuilds: List<GuildBrowseEntry>,
    onCreateGuild: (String) -> Unit,
    onJoinGuild: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    var guildNameInput by remember { mutableStateOf("") }

    Column(modifier = modifier.fillMaxSize().padding(20.dp)) {
        Text(text = "Guild", style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.height(16.dp))

        Text(text = "Create a Guild", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = guildNameInput,
            onValueChange = { guildNameInput = it },
            label = { Text("Guild name") },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(8.dp))
        Button(
            onClick = { onCreateGuild(guildNameInput) },
            enabled = guildNameInput.length in 3..24,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Create Guild")
        }

        Spacer(modifier = Modifier.height(24.dp))
        Text(text = "Or Join an Existing Guild", style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.height(8.dp))

        if (browsableGuilds.isEmpty()) {
            Text(text = "No guilds to join yet.", style = MaterialTheme.typography.bodyMedium)
        } else {
            LazyColumn {
                items(browsableGuilds) { guild ->
                    Row(
                        modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column {
                            Text(text = guild.name, style = MaterialTheme.typography.bodyLarge)
                            Text(
                                text = "Tier " + guild.tier + " - " + guild.memberCount + "/20 members",
                                style = MaterialTheme.typography.bodySmall
                            )
                        }
                        Button(onClick = { onJoinGuild(guild.id) }, enabled = guild.memberCount < 20) {
                            Text("Join")
                        }
                    }
                }
            }
        }
    }
}
'''

with open(path, "w") as f:
    f.write(content)

print("OK: created " + path)
