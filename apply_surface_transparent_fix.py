path = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
with open(path, "r") as f:
    content = f.read()

# Add Color import if not already present.
old_import = "import androidx.compose.foundation.layout.Box\n"
new_import = "import androidx.compose.foundation.layout.Box\nimport androidx.compose.ui.graphics.Color\n"
if old_import in content:
    assert content.count(old_import) == 1, "Box import anchor not found or not unique"
    content = content.replace(old_import, new_import, 1)
else:
    # Import ordering may differ - fall back to appending near the theme import.
    anchor = "import com.yourname.idlerpg.ui.theme.appPatternBackground\n"
    assert content.count(anchor) == 1, "appPatternBackground import anchor not found"
    content = content.replace(anchor, anchor + "import androidx.compose.ui.graphics.Color\n", 1)

# Surface paints its own opaque background AFTER the caller's modifier, which was silently
# covering our custom pattern everywhere except where a child composable drew over it again.
# Telling Surface not to paint its own fill lets the pattern actually show through.
old_surface = "            Surface(modifier = Modifier.fillMaxSize().appPatternBackground()) {"
new_surface = "            Surface(modifier = Modifier.fillMaxSize().appPatternBackground(), color = Color.Transparent) {"
assert content.count(old_surface) == 1, "Surface line not found or not unique"
content = content.replace(old_surface, new_surface, 1)

with open(path, "w") as f:
    f.write(content)

print("OK: MainActivity.kt patched (Surface set transparent so the pattern actually shows through everywhere).")
