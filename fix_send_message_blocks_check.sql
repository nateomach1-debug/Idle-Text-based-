-- fix_send_message_blocks_check.sql
-- Root cause (confirmed via live test): blocking a character hid their DM
-- from view (blockCharacter() only affects client-side fetch filtering) but
-- never stopped them from sending - send_chat_message checks mutes and
-- channel participation, but never touches the blocks table at all.
--
-- Fix: for DM channels, look up the other participant in the channel and
-- block the send if either side has blocked the other.

CREATE OR REPLACE FUNCTION public.send_chat_message(p_character_id uuid, p_channel_id uuid, p_content text)
 RETURNS chat_messages
 LANGUAGE plpgsql
 SECURITY DEFINER
AS $function$
declare
    v_message public.chat_messages;
    v_channel_type public.channel_type;
    v_is_participant boolean;
    v_mute_expires timestamptz;
    v_other_character_id uuid;
begin
    if not public.character_owned_by_caller(p_character_id) then
        raise exception 'Character does not belong to caller.';
    end if;

    select expires_at into v_mute_expires
        from public.mutes
        where character_id = p_character_id
          and (expires_at is null or expires_at > now())
        limit 1;
    if found then
        raise exception 'You are muted%',
            case when v_mute_expires is not null then ' until ' || v_mute_expires else '' end;
    end if;

    if trim(p_content) = '' then
        raise exception 'Message cannot be empty.';
    end if;

    select type into v_channel_type from public.chat_channels where id = p_channel_id;
    if v_channel_type is null then
        raise exception 'Channel not found.';
    end if;

    if v_channel_type in ('GUILD', 'DM') then
        select exists (
            select 1 from public.chat_channel_participants
            where channel_id = p_channel_id and character_id = p_character_id
        ) into v_is_participant;
        if not v_is_participant then
            raise exception 'Not a participant of this channel.';
        end if;
    end if;

    -- NEW: for DMs, block the send if either side has blocked the other.
    if v_channel_type = 'DM' then
        select character_id into v_other_character_id
        from public.chat_channel_participants
        where channel_id = p_channel_id and character_id != p_character_id
        limit 1;

        if v_other_character_id is not null and exists (
            select 1 from public.blocks
            where (blocker_character_id = p_character_id and blocked_character_id = v_other_character_id)
               or (blocker_character_id = v_other_character_id and blocked_character_id = p_character_id)
        ) then
            raise exception 'You cannot message this character.';
        end if;
    end if;

    insert into public.chat_messages (id, channel_id, sender_character_id, content, sent_at, type)
        values (gen_random_uuid(), p_channel_id, p_character_id, p_content, now(), 'NORMAL')
        returning * into v_message;

    return v_message;
end;
$function$
;
