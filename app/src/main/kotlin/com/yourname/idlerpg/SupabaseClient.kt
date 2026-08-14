package com.yourname.idlerpg

import io.github.jan.supabase.auth.Auth
import io.github.jan.supabase.createSupabaseClient
import io.github.jan.supabase.postgrest.Postgrest
import io.github.jan.supabase.realtime.Realtime

// Single shared Supabase client for the whole app - guild/chat multiplayer only.
// Everything else (characters, inventory, skills, combat) stays local and untouched.
object SupabaseClientProvider {
    val client = createSupabaseClient(
        supabaseUrl = BuildConfig.SUPABASE_URL,
        supabaseKey = BuildConfig.SUPABASE_ANON_KEY
    ) {
        install(Auth)
        install(Postgrest)
        install(Realtime)
    }
}

// Tracks whether guild/chat multiplayer features are currently usable. Local
// gameplay never depends on this - it's purely informational for gating
// multiplayer UI until a real session exists.
enum class SupabaseAuthState {
    SIGNED_OUT,
    SIGNING_IN,
    SIGNED_IN,
    ERROR
}
