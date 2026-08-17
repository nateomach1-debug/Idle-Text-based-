-- fix_missing_select_policies_phase_b.sql
-- Same bug class as fix_missing_select_policies.sql (Chat Core): RLS is
-- enabled on these tables but zero SELECT policies exist, so any direct
-- client-side read silently returns empty instead of erroring.
--
-- Confirmed via check_phase_b_rls.sql that mutes, report_appeals, and
-- message_reports have rowsecurity = true but no rows in pg_policies.
--
-- Mirrors the existing authenticated-read pattern used for chat_channels
-- and chat_channel_participants (auth.uid() IS NOT NULL). Moderator-only
-- write actions still go through the SECURITY DEFINER RPCs
-- (admin_mute_character, resolve_report, resolve_appeal, etc.), so this
-- only opens up read access needed for list/status screens.

create policy mutes_select_authenticated
on public.mutes
for select
using (auth.uid() is not null);

create policy report_appeals_select_authenticated
on public.report_appeals
for select
using (auth.uid() is not null);

create policy message_reports_select_authenticated
on public.message_reports
for select
using (auth.uid() is not null);

-- Re-run this after applying, to confirm all 7 tables now show policies:
-- select schemaname, tablename, policyname, cmd
-- from pg_policies
-- where schemaname = 'public'
--   and tablename in ('mutes','report_appeals','message_reports')
-- order by tablename;
