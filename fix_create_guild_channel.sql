-- fix_create_guild_channel.sql
-- Root cause (confirmed via pg_get_functiondef): create_guild() inserts the
-- guild row and the founder's guild_members row, then returns - it never
-- calls get_or_create_guild_channel. That's why no GUILD-type chat_channels
-- row exists for BooziBar (outstanding item #4).
--
-- Fix: add the channel creation inside create_guild itself, in the same
-- transaction, since both functions are SECURITY DEFINER and this mirrors
-- the existing server-enforced pattern used everywhere else in this project.

CREATE OR REPLACE FUNCTION public.create_guild(p_name text, p_founder_character_id uuid)
 RETURNS guilds
 LANGUAGE plpgsql
 SECURITY DEFINER
AS $function$
declare
    v_profile_id uuid := auth.uid();
    v_guild public.guilds;
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

    -- NEW: create the guild's chat channel in the same transaction
    perform public.get_or_create_guild_channel(v_guild.id);

    update public.profiles
        set free_guild_creation_used = true
        where id = v_profile_id and free_guild_creation_used = false;

    return v_guild;
end;
$function$
;

-- Backfill: BooziBar (and any other existing guild) was created before this
-- fix, so it still has no GUILD channel. Run this once to backfill all
-- existing guilds:
select public.get_or_create_guild_channel(id) from public.guilds;

-- Verify after running both statements above:
-- select * from chat_channels where type = 'GUILD';
-- should now show one row per existing guild.
