manifest_path = "app/src/main/AndroidManifest.xml"
with open(manifest_path, encoding="utf-8") as f:
    content = f.read()

anchor = '''    <application
        android:label="Idle RPG"
        android:theme="@android:style/Theme.Material.NoActionBar">'''
count = content.count(anchor)
assert count == 1, f"Expected 1 match, found {count}."
replacement = '''    <application
        android:label="Idle RPG"
        android:allowBackup="false"
        android:theme="@android:style/Theme.Material.NoActionBar">'''
content = content.replace(anchor, replacement, 1)

with open(manifest_path, "w", encoding="utf-8") as f:
    f.write(content)

session_path = "app/src/main/kotlin/com/yourname/idlerpg/SessionManager.kt"
with open(session_path, encoding="utf-8") as f:
    content = f.read()

anchor2 = '''    init {
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()

        prefs = EncryptedSharedPreferences.create(
            context,
            "idlerpg_session",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }'''
count2 = content.count(anchor2)
assert count2 == 1, f"Expected 1 match, found {count2}."
replacement2 = '''    init {
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()

        prefs = try {
            EncryptedSharedPreferences.create(
                context,
                "idlerpg_session",
                masterKey,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
        } catch (e: Exception) {
            // A backup/restore mechanism (Android Auto Backup, Samsung Smart
            // Switch, etc.) can restore this file from a previous install after
            // the Keystore key that encrypted it was deleted at uninstall,
            // making it permanently undecryptable and crashing the app on every
            // launch before it can render. Wipe the corrupted file and start
            // fresh instead of crashing - the account is still recoverable via
            // cloud login regardless of local session state.
            context.deleteSharedPreferences("idlerpg_session")
            EncryptedSharedPreferences.create(
                context,
                "idlerpg_session",
                masterKey,
                EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
            )
        }
    }'''
content = content.replace(anchor2, replacement2, 1)

with open(session_path, "w", encoding="utf-8") as f:
    f.write(content)

print("patch_fix_session_crash_on_restore.py applied cleanly.")
