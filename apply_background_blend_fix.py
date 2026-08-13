import os

# --- 1. Soften the pattern intensity in PatternBackground.kt. ---
pattern_path = "app/src/main/kotlin/com/yourname/idlerpg/PatternBackground.kt"
with open(pattern_path, "r") as f:
    content = f.read()

old_constants = '''private const val PATTERN_LINE_SPACING_DP = 22f
private const val PATTERN_LINE_ALPHA = 0.06f
private const val GRADIENT_BOTTOM_ALPHA = 0.30f'''
new_constants = '''private const val PATTERN_LINE_SPACING_DP = 22f
private const val PATTERN_LINE_ALPHA = 0.045f
private const val GRADIENT_BOTTOM_ALPHA = 0.20f'''
assert content.count(old_constants) == 1, "pattern constants not found or not unique"
content = content.replace(old_constants, new_constants, 1)

with open(pattern_path, "w") as f:
    f.write(content)
print("OK: softened constants in " + pattern_path)

# --- 2. MainActivity.kt: move the background to the outer Surface (paints once, behind
#         everything including the Log Out row at the very top), remove the now-redundant
#         separate background from the inner content Box. ---
ma_path = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
with open(ma_path, "r") as f:
    content = f.read()

old_surface = '''        AppFlowState.InGame -> {
            Surface(modifier = Modifier.fillMaxSize()) {
                Column(modifier = Modifier.fillMaxSize()) {'''
new_surface = '''        AppFlowState.InGame -> {
            Surface(modifier = Modifier.fillMaxSize().appPatternBackground()) {
                Column(modifier = Modifier.fillMaxSize()) {'''
assert content.count(old_surface) == 1, "InGame Surface block not found or not unique"
content = content.replace(old_surface, new_surface, 1)

old_content_box = "                        Box(modifier = Modifier.weight(1f).appPatternBackground()) {\n"
new_content_box = "                        Box(modifier = Modifier.weight(1f)) {\n"
assert content.count(old_content_box) == 1, "content Box not found or not unique"
content = content.replace(old_content_box, new_content_box, 1)

with open(ma_path, "w") as f:
    f.write(content)
print("OK: patched " + ma_path)

# --- 3. SideRail.kt: remove its own opaque fill so the shared background shows through
#         (this is what was causing the vertical seam). ---
sr_path = "app/src/main/kotlin/com/yourname/idlerpg/ui/navigation/SideRail.kt"
if not os.path.exists(sr_path):
    sr_path = "app/src/main/kotlin/com/yourname/idlerpg/SideRail.kt"
with open(sr_path, "r") as f:
    content = f.read()

old_sr_bg = "            .fillMaxHeight()\n            .railPatternBackground()\n            .animateContentSize()"
new_sr_bg = "            .fillMaxHeight()\n            .animateContentSize()"
assert content.count(old_sr_bg) == 1, "SideRail background line not found or not unique"
content = content.replace(old_sr_bg, new_sr_bg, 1)

old_sr_import = "import com.yourname.idlerpg.ui.theme.railPatternBackground\n"
assert content.count(old_sr_import) == 1, "railPatternBackground import not found or not unique in SideRail.kt"
content = content.replace(old_sr_import, "", 1)

with open(sr_path, "w") as f:
    f.write(content)
print("OK: patched " + sr_path)

# --- 4. RecoveryBar.kt: same treatment - drop its own opaque fill so it blends when visible. ---
rb_path = "app/src/main/kotlin/com/yourname/idlerpg/ui/components/RecoveryBar.kt"
if not os.path.exists(rb_path):
    rb_path = "app/src/main/kotlin/com/yourname/idlerpg/RecoveryBar.kt"
with open(rb_path, "r") as f:
    content = f.read()

old_rb_bg = "            .fillMaxWidth()\n            .background(MaterialTheme.colorScheme.surface)\n            .padding(horizontal = 16.dp, vertical = 8.dp),"
new_rb_bg = "            .fillMaxWidth()\n            .padding(horizontal = 16.dp, vertical = 8.dp),"
assert content.count(old_rb_bg) == 1, "RecoveryBar background line not found or not unique"
content = content.replace(old_rb_bg, new_rb_bg, 1)

with open(rb_path, "w") as f:
    f.write(content)
print("OK: patched " + rb_path)
