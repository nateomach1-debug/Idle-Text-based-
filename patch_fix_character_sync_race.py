apply-patch:
    name: Apply Patch Script
    max_build_duration: 10
    scripts:
      - name: Write and run patch script
        script: |
          cat > patch_fix_character_sync_race.py << 'PYEOF'
          path = "app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt"
          with open(path, encoding="utf-8") as f:
              content = f.read()

          anchor_import = "import io.github.jan.supabase.auth.status.SessionStatus"
          count_import = content.count(anchor_import)
          assert count_import == 1, f"Expected 1 match for anchor_import, found {count_import}."
          new_imports = []
          if "import kotlinx.coroutines.withTimeoutOrNull" not in content:
              new_imports.append("import kotlinx.coroutines.withTimeoutOrNull")
          if "import kotlinx.coroutines.flow.first" not in content:
              new_imports.append("import kotlinx.coroutines.flow.first")
          if new_imports:
              replacement_import = anchor_import + "\n" + "\n".join(new_imports)
              content = content.replace(anchor_import, replacement_import, 1)

          anchor2 = '''            viewModelScope.launch {
                          val result = SupabaseCharacterRepository.getOrCreateCharacter(characterId, selectedCharacter.displayName)
                          result.onFailure { _characterSyncError.value = it.message ?: it.toString() }'''
          count2 = content.count(anchor2)
          assert count2 == 1, f"Expected 1 match for anchor2, found {count2}."
          replacement2 = '''            viewModelScope.launch {
                          val authState = withTimeoutOrNull(10_000L) {
                              supabaseAuthState.first { it != SupabaseAuthState.SIGNING_IN }
                          }
                          if (authState != SupabaseAuthState.SIGNED_IN) {
                              _characterSyncError.value = "Not signed in to multiplayer services yet - character sync will retry on next action."
                              return@launch
                          }
                          val result = SupabaseCharacterRepository.getOrCreateCharacter(characterId, selectedCharacter.displayName)
                          result.onFailure { _characterSyncError.value = it.message ?: it.toString() }'''
          content = content.replace(anchor2, replacement2, 1)

          with open(path, "w", encoding="utf-8") as f:
              f.write(content)

          print("patch_fix_character_sync_race.py applied cleanly.")
          PYEOF
          python3 patch_fix_character_sync_race.py
          git config user.email "codemagic@example.com"
          git config user.name "Codemagic Bot"
          git add app/src/main/kotlin/com/yourname/idlerpg/GameViewModel.kt
          git commit -m "Fix character sync race condition on cold start"
          git push
