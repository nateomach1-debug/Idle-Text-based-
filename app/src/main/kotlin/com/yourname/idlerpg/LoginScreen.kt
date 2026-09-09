package com.yourname.idlerpg.ui.screens

import com.yourname.idlerpg.ui.theme.overrideColor

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp

// =========================================================
// LOGIN SCREEN
// Email + password, with a toggle to switch into account
// creation mode. On success, caller decides whether to route
// to Character Creation or Character Selection.
// =========================================================

@Composable
fun LoginScreen(
    isCreatingAccount: Boolean,
    onToggleMode: () -> Unit,
    errorMessage: String?,
    onLogin: (email: String, password: String) -> Unit,
    onCreateAccount: (email: String, username: String, password: String) -> Unit,
    modifier: Modifier = Modifier
) {
    var email by remember { mutableStateOf("") }
    var username by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = if (isCreatingAccount) "Create Account" else "Log In",
            style = MaterialTheme.typography.headlineMedium
        )

        Spacer(modifier = Modifier.height(24.dp))

        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Email") },
            modifier = Modifier.fillMaxWidth()
        )

        Spacer(modifier = Modifier.height(12.dp))

        if (isCreatingAccount) {
            OutlinedTextField(
                value = username,
                onValueChange = { username = it },
                label = { Text("Username") },
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(12.dp))
        }

        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Password") },
            visualTransformation = PasswordVisualTransformation(),
            modifier = Modifier.fillMaxWidth()
        )

        errorMessage?.let {
            Spacer(modifier = Modifier.height(8.dp))
            Text(text = it, style = MaterialTheme.typography.labelSmall, color = overrideColor(MaterialTheme.colorScheme.error))
        }

        Spacer(modifier = Modifier.height(20.dp))

        Button(
            onClick = {
                if (isCreatingAccount) {
                    onCreateAccount(email, username, password)
                } else {
                    onLogin(email, password)
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(text = if (isCreatingAccount) "Create Account" else "Log In")
        }

        Spacer(modifier = Modifier.height(12.dp))

        TextButton(onClick = onToggleMode) {
            Text(text = if (isCreatingAccount) "Already have an account? Log In" else "Need an account? Create one")
        }
    }
}
