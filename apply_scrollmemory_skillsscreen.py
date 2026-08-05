#!/usr/bin/env python3
"""
Scroll-memory patch, part 1: SkillsScreen.kt

SkillsScreen/SkillsListView/SkillsGridView now accept an optional
LazyListState/LazyGridState instead of each LazyColumn/LazyVerticalGrid
creating its own default state. The default is still a fresh
rememberLazyListState()/rememberLazyGridState() (so nothing breaks if
called without one), but MainActivity.kt will pass in a state hoisted at
the app-root level so it survives navigating away from and back to the
Skills tab (which fully disposes/recreates SkillsScreen under the current
`when(destination)` navigation pattern).

Run from repo root:
    python3 apply_scrollmemory_skillsscreen.py
"""
import sys
from pathlib import Path

TARGET = Path("app/src/main/kotlin/com/yourname/idlerpg/SkillsScreen.kt")


def fail(msg):
    print(f"FAILED: {msg}")
    sys.exit(1)


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        fail(f"expected exactly 1 occurrence of [{label}], found {count}")
    return text.replace(old, new, 1)


def main():
    if not TARGET.exists():
        fail(f"{TARGET} not found -- run this from the repo root")

    text = TARGET.read_text()
    original = text

    if "listState: LazyListState" in text:
        fail("listState parameter already present -- patch may already be applied")

    # 1. Imports for Lazy state types
    text = replace_once(
        text,
        (
            "import androidx.compose.foundation.lazy.LazyColumn\n"
            "import androidx.compose.foundation.lazy.items\n"
        ),
        (
            "import androidx.compose.foundation.lazy.LazyColumn\n"
            "import androidx.compose.foundation.lazy.LazyListState\n"
            "import androidx.compose.foundation.lazy.items\n"
            "import androidx.compose.foundation.lazy.rememberLazyListState\n"
        ),
        "LazyColumn import block",
    )
    text = replace_once(
        text,
        (
            "import androidx.compose.foundation.lazy.grid.GridCells\n"
            "import androidx.compose.foundation.lazy.grid.GridItemSpan\n"
            "import androidx.compose.foundation.lazy.grid.LazyVerticalGrid\n"
            "import androidx.compose.foundation.lazy.grid.items\n"
        ),
        (
            "import androidx.compose.foundation.lazy.grid.GridCells\n"
            "import androidx.compose.foundation.lazy.grid.GridItemSpan\n"
            "import androidx.compose.foundation.lazy.grid.LazyGridState\n"
            "import androidx.compose.foundation.lazy.grid.LazyVerticalGrid\n"
            "import androidx.compose.foundation.lazy.grid.items\n"
            "import androidx.compose.foundation.lazy.grid.rememberLazyGridState\n"
        ),
        "LazyVerticalGrid import block",
    )

    # 2. SkillsScreen() signature + call sites
    text = replace_once(
        text,
        (
            "@Composable\n"
            "fun SkillsScreen(\n"
            "    allSkills: Map<String, SkillSummary>,\n"
            "    onSkillSelected: (String) -> Unit,\n"
            "    modifier: Modifier = Modifier\n"
            ") {\n"
        ),
        (
            "@Composable\n"
            "fun SkillsScreen(\n"
            "    allSkills: Map<String, SkillSummary>,\n"
            "    onSkillSelected: (String) -> Unit,\n"
            "    modifier: Modifier = Modifier,\n"
            "    listState: LazyListState = rememberLazyListState(),\n"
            "    gridState: LazyGridState = rememberLazyGridState()\n"
            ") {\n"
        ),
        "SkillsScreen() signature",
    )
    text = replace_once(
        text,
        (
            "        when (viewMode) {\n"
            "            SkillsViewMode.LIST -> SkillsListView(sections, onSkillSelected)\n"
            "            SkillsViewMode.GRID -> SkillsGridView(sections, onSkillSelected)\n"
            "        }\n"
        ),
        (
            "        when (viewMode) {\n"
            "            SkillsViewMode.LIST -> SkillsListView(sections, onSkillSelected, listState)\n"
            "            SkillsViewMode.GRID -> SkillsGridView(sections, onSkillSelected, gridState)\n"
            "        }\n"
        ),
        "viewMode when-block call sites",
    )

    # 3. SkillsListView: accept + use listState
    text = replace_once(
        text,
        (
            "@Composable\n"
            "private fun SkillsListView(sections: List<SkillGroupSection>, onSkillSelected: (String) -> Unit) {\n"
            "    LazyColumn(verticalArrangement = Arrangement.spacedBy(4.dp)) {\n"
        ),
        (
            "@Composable\n"
            "private fun SkillsListView(\n"
            "    sections: List<SkillGroupSection>,\n"
            "    onSkillSelected: (String) -> Unit,\n"
            "    listState: LazyListState\n"
            ") {\n"
            "    LazyColumn(state = listState, verticalArrangement = Arrangement.spacedBy(4.dp)) {\n"
        ),
        "SkillsListView signature + LazyColumn state",
    )

    # 4. SkillsGridView: accept + use gridState
    text = replace_once(
        text,
        (
            "@Composable\n"
            "private fun SkillsGridView(sections: List<SkillGroupSection>, onSkillSelected: (String) -> Unit) {\n"
            "    LazyVerticalGrid(\n"
            "        columns = GridCells.Fixed(3),\n"
        ),
        (
            "@Composable\n"
            "private fun SkillsGridView(\n"
            "    sections: List<SkillGroupSection>,\n"
            "    onSkillSelected: (String) -> Unit,\n"
            "    gridState: LazyGridState\n"
            ") {\n"
            "    LazyVerticalGrid(\n"
            "        state = gridState,\n"
            "        columns = GridCells.Fixed(3),\n"
        ),
        "SkillsGridView signature + LazyVerticalGrid state",
    )

    if text == original:
        fail("no changes were made -- aborting")

    TARGET.write_text(text)
    print(f"OK: patched {TARGET}")


if __name__ == "__main__":
    main()
