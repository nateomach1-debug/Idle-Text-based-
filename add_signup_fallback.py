import pathlib

p = pathlib.Path("app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt")
text = p.read_text()

old = """                } else {
                    auth.signInWith(io.github.jan.supabase.auth.providers.builtin.Email) {
                        this.email = email
                        this.password = password
                    }
                }"""

if text.count(old) != 1:
    print(f"FAILED: expected 1 occurrence, found {text.count(old)}")
else:
    new = """                } else {
                    try {
                        auth.signInWith(io.github.jan.supabase.auth.providers.builtin.Email) {
                            this.email = email
                            this.password = password
                        }
                    } catch (signInError: Exception) {
                        // Local account existed before Supabase sync was added - no
                        // matching Supabase account exists yet. Lazily create one now
                        // with the same credentials, so future logins sign in normally.
                        auth.signUpWith(io.github.jan.supabase.auth.providers.builtin.Email) {
                            this.email = email
                            this.password = password
                        }
                    }
                }"""
    text = text.replace(old, new, 1)
    p.write_text(text)
    print("FIXED: sign-in now falls back to sign-up on failure")
