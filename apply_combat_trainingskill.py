import re

path = "app/src/main/kotlin/com/yourname/idlerpg/CombatSystem.kt"
with open(path, "r") as f:
    content = f.read()

# --- 1. Add CombatSkillRules object right after the CombatStyle-using Weapon/Spell/SpellBook block,
#         before LootEntry. Anchored on the SpellBook closing brace + availableSpells line. ---
anchor1 = '    fun availableSpells(magicLevel: Int): List<Spell> = spells.filter { it.levelRequired <= magicLevel }\n}\n'
assert content.count(anchor1) == 1, "anchor1 not found or not unique"

skill_rules = anchor1 + '''
// Which combat skills a character can select to train, based on the equipped
// weapon's style. Defense is always trainable regardless of weapon style,
// matching the classic "defensive style still uses your main weapon" model.
object CombatSkillRules {
    fun allowedTrainingSkills(style: CombatStyle): List<SkillType> = when (style) {
        CombatStyle.MELEE -> listOf(SkillType.ATTACK, SkillType.STRENGTH, SkillType.DEFENSE)
        CombatStyle.RANGED -> listOf(SkillType.ARCHERY, SkillType.DEFENSE)
        CombatStyle.MAGIC -> listOf(SkillType.MAGIC, SkillType.DEFENSE)
    }
}
'''
content = content.replace(anchor1, skill_rules, 1)

# --- 2. CombatLoadout gains trainingSkill. ---
old_loadout = '''data class CombatLoadout(
    val style: CombatStyle,
    val equippedWeapon: Weapon?,
    val equippedSpell: Spell?,
    val autoHealThresholdPercent: Int,
    val autoFleeThresholdPercent: Int
)'''
new_loadout = '''data class CombatLoadout(
    val style: CombatStyle,
    val trainingSkill: SkillType,
    val equippedWeapon: Weapon?,
    val equippedSpell: Spell?,
    val autoHealThresholdPercent: Int,
    val autoFleeThresholdPercent: Int
)'''
assert content.count(old_loadout) == 1, "CombatLoadout block not found or not unique"
content = content.replace(old_loadout, new_loadout, 1)

# --- 3. enterZone: rename characterLevel -> trainingSkillLevel, clarify via doc comment. ---
old_enter = '''    fun enterZone(characterId: String, zoneId: String, characterLevel: Int): ServiceResult<CombatSession> {
        val state = stateFor(characterId)
        if (state.recovery.isRecovering()) {
            return ServiceResult.Failure("Cannot enter combat while recovering.")
        }
        val zone = ZoneCatalog.zones.find { it.id == zoneId }
            ?: return ServiceResult.Failure("Zone not found.")
        if (zone.levelRequirement > characterLevel) {
            return ServiceResult.Failure("Requires level " + zone.levelRequirement + " to enter " + zone.name + ".")
        }'''
new_enter = '''    // trainingSkillLevel must be the level of whichever SkillType the character
    // currently has selected to train (loadout.trainingSkill) - NOT a blended
    // "character level". Each combat skill unlocks zones independently.
    fun enterZone(characterId: String, zoneId: String, trainingSkillLevel: Int): ServiceResult<CombatSession> {
        val state = stateFor(characterId)
        if (state.recovery.isRecovering()) {
            return ServiceResult.Failure("Cannot enter combat while recovering.")
        }
        val zone = ZoneCatalog.zones.find { it.id == zoneId }
            ?: return ServiceResult.Failure("Zone not found.")
        if (zone.levelRequirement > trainingSkillLevel) {
            return ServiceResult.Failure("Requires level " + zone.levelRequirement + " to enter " + zone.name + ".")
        }'''
assert content.count(old_enter) == 1, "enterZone block not found or not unique"
content = content.replace(old_enter, new_enter, 1)

with open(path, "w") as f:
    f.write(content)

print("OK: CombatSystem.kt patched (CombatSkillRules added, CombatLoadout.trainingSkill added, enterZone param renamed).")
