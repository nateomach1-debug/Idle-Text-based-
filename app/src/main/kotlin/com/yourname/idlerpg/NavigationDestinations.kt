package com.yourname.idlerpg.ui.navigation

// =========================================================
// The 7 top-level destinations shown in the collapsible side rail.
// Icon names are placeholders referencing Material Icons -- swap
// for custom skill-appropriate icons later without touching
// anything else, since screens only reference this enum.
// =========================================================

enum class AppDestination(val label: String, val iconName: String) {
    HOME("Home", "person"),
    SKILLS("Skills", "auto_awesome"),
    COMBAT("Combat", "swords"),
    INVENTORY("Inventory", "backpack"),
    MARKET("Market", "storefront"),
    GUILD("Guild", "flag"),
    MODERATION("Moderation", "shield_person")
}
