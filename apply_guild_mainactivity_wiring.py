path = "app/src/main/kotlin/com/yourname/idlerpg/MainActivity.kt"
with open(path, "r") as f:
    content = f.read()

old_guild_block = '''                            AppDestination.GUILD -> {
                                GuildHomeScreen(
                                    state = demoGuildState(),
                                    leaderboardEntries = demoLeaderboard(),
                                    leaderboardShowingDaily = leaderboardShowingDaily,
                                    onToggleLeaderboardPeriod = { leaderboardShowingDaily = !leaderboardShowingDaily },
                                    onMemberTapped = { selectedGuildMember = it },
                                    onContributeToEvent = { },
                                    onCastVote = { }
                                )

                                selectedGuildMember?.let { member ->
                                    MemberActionPopup(
                                        member = member,
                                        viewerRole = GuildMemberRole.LEADER,
                                        onDismiss = { selectedGuildMember = null },
                                        onKick = { selectedGuildMember = null },
                                        onPromote = { selectedGuildMember = null },
                                        onDemote = { selectedGuildMember = null },
                                        onInitiateVote = { selectedGuildMember = null }
                                    )
                                }
                            }'''
new_guild_block = '''                            AppDestination.GUILD -> {
                                val currentGuildHomeState by gameViewModel.guildHomeState.collectAsState()
                                val currentGuildLeaderboard by gameViewModel.guildLeaderboard.collectAsState()
                                val currentBrowsableGuilds by gameViewModel.browsableGuilds.collectAsState()

                                LaunchedEffect(Unit) { gameViewModel.refreshGuildHome() }

                                val guildState = currentGuildHomeState
                                if (guildState == null) {
                                    GuildCreateJoinScreen(
                                        browsableGuilds = currentBrowsableGuilds,
                                        onCreateGuild = { name -> gameViewModel.createGuild(name) },
                                        onJoinGuild = { guildId -> gameViewModel.joinGuild(guildId) }
                                    )
                                } else {
                                    GuildHomeScreen(
                                        state = guildState,
                                        leaderboardEntries = currentGuildLeaderboard,
                                        leaderboardShowingDaily = leaderboardShowingDaily,
                                        onToggleLeaderboardPeriod = { leaderboardShowingDaily = !leaderboardShowingDaily },
                                        onMemberTapped = { selectedGuildMember = it },
                                        onContributeToEvent = { },
                                        onCastVote = { }
                                    )

                                    selectedGuildMember?.let { member ->
                                        MemberActionPopup(
                                            member = member,
                                            viewerRole = guildState.viewerRole,
                                            onDismiss = { selectedGuildMember = null },
                                            onKick = {
                                                gameViewModel.kickGuildMember(member.characterId)
                                                selectedGuildMember = null
                                            },
                                            onPromote = {
                                                when (member.role) {
                                                    GuildMemberRole.MEMBER -> gameViewModel.promoteGuildMemberToOfficer(member.characterId)
                                                    GuildMemberRole.OFFICER -> gameViewModel.promoteGuildMemberToLeader(member.characterId)
                                                    GuildMemberRole.LEADER -> {}
                                                }
                                                selectedGuildMember = null
                                            },
                                            onDemote = { selectedGuildMember = null },
                                            onInitiateVote = { selectedGuildMember = null }
                                        )
                                    }
                                }
                            }'''
assert content.count(old_guild_block) == 1, "GUILD destination block not found or not unique"
content = content.replace(old_guild_block, new_guild_block, 1)

with open(path, "w") as f:
    f.write(content)

print("OK: MainActivity.kt patched (GUILD destination wired to real Supabase-backed state, create/join branch added).")
