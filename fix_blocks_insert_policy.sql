-- fix_blocks_insert_policy.sql
-- Root cause (confirmed via live test + pg_policies check): blocks only ever
-- had a SELECT policy ("blocks visible to the blocker"). No INSERT policy
-- existed, so blockCharacter()'s insert was silently RLS-denied every time -
-- wrapped in runCatching client-side, so it just looked like "nothing
-- happened" with no visible error.

create policy "blocks insertable by the blocker"
on public.blocks
for insert
with check (
  exists (
    select 1 from public.characters ch
    where ch.id = blocks.blocker_character_id and ch.profile_id = auth.uid()
  )
);

-- Verify after running:
-- select schemaname, tablename, policyname, cmd
-- from pg_policies
-- where schemaname = 'public' and tablename = 'blocks'
-- order by cmd;
-- should now show both SELECT and INSERT policies.
