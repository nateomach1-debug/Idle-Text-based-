"""
Fix: signup path has no fallback when the account already exists.

The existing login path (isNewAccount = false) already has a fallback:
try signIn, and if that fails (local account predates Supabase sync),
fall back to signUp. But the signup path (isNewAccount = true) has no
matching fallback the other way - if signUp fails because the account
already exists on the server (e.g. user got a new phone, lost their
local account, and re-registered with the same email), the error just
propagates and nothing downstream (character sync, etc.) has a valid
session to work with.

This adds the mirror-image fallback: on signup, if it fails specifically
because the account already exists, retry as a sign-in with the same
credentials instead of erroring out.

Guarded with asserts.
"""

import os

BASE = "app/src/main/kotlin/com/yourname/idlerpg"
path = os.path.join(BASE, "GameViewModel.kt")

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = (
    "                if (isNewAccount) {\n"
    "                    auth.signUpWith(io.github.jan.supabase.auth.providers.builtin.Email) {\n"
    "                        this.email = email\n"
    "                        this.password = password\n"
    "                    }\n"
    "                } else {\n"
)
new = (
    "                if (isNewAccount) {\n"
    "                    try {\n"
    "                        auth.signUpWith(io.github.jan.supabase.auth.providers.builtin.Email) {\n"
    "                            this.email = email\n"
    "                            this.password = password\n"
    "                        }\n"
    "                    } catch (signUpError: Exception) {\n"
    "                        val message = signUpError.message ?: \"\"\n"
    "                        if (message.contains(\"user_already_exists\", ignoreCase = true) ||\n"
    "                            message.contains(\"already registered\", ignoreCase = true)\n"
    "                        ) {\n"
    "                            // Account already exists on the server (e.g. new phone, lost\n"
    "                            // local account, re-registered with the same email) - log in\n"
    "                            // to that existing account instead of failing outright.\n"
    "                            auth.signInWith(io.github.jan.supabase.auth.providers.builtin.Email) {\n"
    "                                this.email = email\n"
    "                                this.password = password\n"
    "                            }\n"
    "                        } else {\n"
    "                            throw signUpError\n"
    "                        }\n"
    "                    }\n"
    "                } else {\n"
)

assert old in content, "isNewAccount signup anchor not found"
assert content.count(old) == 1, "isNewAccount signup anchor not unique"
content = content.replace(old, new)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patched GameViewModel.kt: signup now falls back to sign-in when the account already exists.")
