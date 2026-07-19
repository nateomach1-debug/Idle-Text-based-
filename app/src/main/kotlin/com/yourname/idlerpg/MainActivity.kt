package com.yourname.idlerpg

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import com.yourname.idlerpg.ui.navigation.AppDestination
import com.yourname.idlerpg.ui.navigation.SideRail
import com.yourname.idlerpg.ui.screens.HomeScreen
import com.yourname.idlerpg.ui.screens.HomeScreenState
import com.yourname.idlerpg.ui.theme.IdleRpgTheme
import java.time.Instant

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            IdleRpgTheme {
                AppRoot()
            }
        }
    }
}

@Composable
fun AppRoot() {
    var currentDestination by remember { mutableStateOf(AppDestination.HOME) }

    // Placeholder state -- will be replaced by real ViewModel-driven
    // state pulling from the backend services once they're wired in.
    val homeState = remember {
        HomeScreenState(
            queueLabel = "Mining Iron Ore",
            queueEndsAt = Instant.now().plusSeconds(90),
            softCurrency = 1250,
            premiumCurrency = 40,
            currentHp = 80,
            maxHp = 100,
            isRecovering = false,
            pendingLootCount = 3,
            unreadNotificationCount = 2
        )
    }

    Surface(modifier = Modifier.fillMaxSize()) {
        Row(modifier = Modifier.fillMaxSize()) {
            SideRail(
                currentDestination = currentDestination,
                onDestinationSelected = { currentDestination = it },
                badgedDestinations = setOf(AppDestination.CHAT, AppDestination.GUILD)
            )

            when (currentDestination) {
                AppDestination.HOME -> HomeScreen(
                    state = homeState,
                    onCollectLoot = { /* wire to CombatService.collectLoot later */ }
                )
                else -> androidx.compose.material3.Text(
                    text = currentDestination.label + " screen coming soon",
                    modifier = Modifier.fillMaxSize()
                )
            }
        }
    }
}
