-- These three tables have RLS enabled but were missing SELECT policies
-- entirely, meaning any direct client-side read (as opposed to a
-- SECURITY DEFINER RPC call, which bypasses RLS) silently returned
-- zero rows instead of erroring. None of this data is sensitive -
-- channel list, channel participants, and character display names
-- are all fine to be readable by any signed-in player.

create policy chat_channels_select_authenticated on public.chat_channels
    for select using (auth.uid() is not null);

create policy chat_channel_participants_select_authenticated on public.chat_channel_participants
    for select using (auth.uid() is not null);

create policy characters_select_authenticated on public.characters
    for select using (auth.uid() is not null);
