-- check_phase_b_rls.sql
-- Purpose: verify RLS enabled/policy status on every table Phase B moderation
-- screens will read directly, BEFORE assuming any bug is broken code vs missing policy.
-- Run this in the Supabase SQL editor and paste the full output into a
-- phase_b_rls_result.txt dump (see git commands below).

-- 1. Which tables have RLS enabled at all
select
  schemaname,
  tablename,
  rowsecurity as rls_enabled
from pg_tables
where schemaname = 'public'
  and tablename in (
    'mutes',
    'report_appeals',
    'message_reports',
    'blocks',
    'chat_channels',
    'chat_channel_participants',
    'characters'
  )
order by tablename;

-- 2. Every policy that currently exists on those tables, and what it allows
select
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual,
  with_check
from pg_policies
where schemaname = 'public'
  and tablename in (
    'mutes',
    'report_appeals',
    'message_reports',
    'blocks',
    'chat_channels',
    'chat_channel_participants',
    'characters'
  )
order by tablename, policyname;

-- 3. Sanity check: is is_moderator actually set on the test profile
select id, is_moderator
from profiles
where id = '4453e95f-80e0-4aa3-b62f-479acdafa6a7';

-- 4. Sanity check: does a GUILD-type chat channel exist for BooziBar
-- (outstanding item #4 from next_session_prompt.txt)
select * from chat_channels where type = 'GUILD';
