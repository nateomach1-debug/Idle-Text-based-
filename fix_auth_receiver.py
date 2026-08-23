"""
Fix: 'auth' is an extension property (SupabaseClient.auth) - it only
resolved bare inside syncSupabaseAuth() because that function has its
own local receiver in scope. My new attemptCloudRecoveryLogin() function
doesn't, so it needs the fully-qualified SupabaseClientProvider.client.auth,
matching the pattern already used in SupabaseCharacterRepository.kt.

Guarded with asserts.
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
path = os.path.join(BASE, "GameViewModel.kt")

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = (
    "        try {\n"
    "            auth.signInWith(io.github.jan.supabase.auth.providers.builtin.Email) {\n"
    "                this.email = email\n"
    "                this.password = password\n"
    "            }\n"
    "        } catch (e: Exception) {\n"
    "            _characterSyncError.value = \"No local account found, and no matching cloud account either.\"\n"
    "            return@launch\n"
    "        }\n"
)
new = (
    "        try {\n"
    "            SupabaseClientProvider.client.auth.signInWith(io.github.jan.supabase.auth.providers.builtin.Email) {\n"
    "                this.email = email\n"
    "                this.password = password\n"
    "            }\n"
    "        } catch (e: Exception) {\n"
    "            _characterSyncError.value = \"No local account found, and no matching cloud account either.\"\n"
    "            return@launch\n"
    "        }\n"
)

assert old in content, "auth.signInWith anchor not found - may already be fixed"
assert content.count(old) == 1, "anchor not unique"
content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched GameViewModel.kt: auth.signInWith -> SupabaseClientProvider.client.auth.signInWith")
