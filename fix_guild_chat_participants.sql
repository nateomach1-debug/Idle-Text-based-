-- fix_guild_chat_participants.sql
-- Root cause (confirmed via live "Not a participant of this channel" error,
-- code P0001, from send_chat_message): get_or_create_guild_channel creates
-- the GUILD chat_channels row, but nothing ever inserts a matching row into
-- chat_channel_participants for guild members - neither on guild creation
-- nor on joining. So every guild's chat has always been unusable for
-- everyone, not just Boozi.

-- 1. create_guild: add founder as a participant of the new guild channel.
CREATE OR REPLACE FUNCTION public.create_guild(p_name text, p_founder_character_id uuid)
 RETURNS guilds
 LANGUAGE plpgsql
 SECURITY DEFINER
AS $function$
declare
    v_profile_id uuid := auth.uid();
    v_guild public.guilds;
    v_channel_id uuid;
begin
    if v_profile_id is null then
        raise exception 'Not authenticated';
    end if;

    if not exists (
        select 1 from public.characters
        where id = p_founder_character_id and profile_id = v_profile_id
    ) then
        raise exception 'Character does not belong to caller';
    end if;

    if length(p_name) < 3 or length(p_name) > 24 then
        raise exception 'Guild name must be between 3 and 24 characters';
    end if;

    insert into public.guilds (name, leader_character_id)
        values (p_name, p_founder_character_id)
        returning * into v_guild;

    insert into public.guild_members (guild_id, character_id, role)
        values (v_guild.id, p_founder_character_id, 'LEADER');

    v_channel_id := public.get_or_create_guild_channel(v_guild.id);

    insert into public.chat_channel_participants (channel_id, character_id)
        values (v_channel_id, p_founder_character_id)
        on conflict do nothing;

    update public.profiles
        set free_guild_creation_used = true
        where id = v_profile_id and free_guild_creation_used = false;

    return v_guild;
end;
$function$
;

-- 2. join_guild: add the joining character as a participant of the guild channel.
CREATE OR REPLACE FUNCTION public.join_guild(p_guild_id uuid, p_character_id uuid)
 RETURNS void
 LANGUAGE plpgsql
 SECURITY DEFINER
AS $function$
declare
    v_profile_id uuid := auth.uid();
    v_member_count integer;
    v_channel_id uuid;
begin
    if v_profile_id is null then
        raise exception 'Not authenticated';
    end if;

    if not exists (
        select 1 from public.characters
        where id = p_character_id and profile_id = v_profile_id
    ) then
        raise exception 'Character does not belong to caller';
    end if;

    if exists (select 1 from public.guild_members where character_id = p_character_id) then
        raise exception 'Character is already in a guild';
    end if;

    if not exists (select 1 from public.guilds where id = p_guild_id) then
        raise exception 'Guild not found';
    end if;

    select count(*) into v_member_count from public.guild_members where guild_id = p_guild_id;
    if v_member_count >= 20 then
        raise exception 'Guild is at max capacity (20)';
    end if;

    insert into public.guild_members (guild_id, character_id, role)
        values (p_guild_id, p_character_id, 'MEMBER');

    v_channel_id := public.get_or_create_guild_channel(p_guild_id);

    insert into public.chat_channel_participants (channel_id, character_id)
        values (v_channel_id, p_character_id)
        on conflict do nothing;
end;
$function$
;

-- 3. Backfill: every existing guild member (e.g. Boozi in BooziBar) is
-- missing their participant row. Add them all now.
insert into public.chat_channel_participants (channel_id, character_id)
select cc.id, gm.character_id
from public.guild_members gm
join public.chat_channels cc on cc.type = 'GUILD' and cc.guild_id = gm.guild_id
on conflict do nothing;

-- Verify after running all three statements above:
-- select * from chat_channel_participants;
-- should now include a row for Boozi's guild channel.
