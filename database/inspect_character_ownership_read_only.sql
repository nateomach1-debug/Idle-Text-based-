-- READ-ONLY CHARACTER OWNERSHIP, GUILD, AND DELETE-IMPACT AUDIT
-- Run in Supabase SQL Editor while signed into the correct project.
-- This file contains SELECT statements only. It does not modify data, schema,
-- policies, functions, memberships, or character records.
--
-- Verified local IDs:
-- Knight: e6bc06bf-75c2-4108-bb13-d84c477520e0
-- Mage:   90b7b7c3-ecaa-463d-9f12-ac87bd9fc375
-- Verified remote IDs:
-- Knight: 3b25c2d5-d3e3-4c02-9c8f-d7b08f156b0e
-- Mage:   3b39b880-cf5d-418f-af1e-c22fd6e9995b

-- 1. Confirm the two public.characters rows (Knight is currently reported
-- missing by the app diagnostic).
SELECT
    c.id AS remote_character_id,
    c.local_character_id,
    c.profile_id,
    c.display_name,
    to_jsonb(c) - 'profile_id' AS character_metadata_without_profile_id
FROM public.characters AS c
WHERE c.id IN (
    '3b25c2d5-d3e3-4c02-9c8f-d7b08f156b0e'::uuid,
    '3b39b880-cf5d-418f-af1e-c22fd6e9995b'::uuid
)
   OR c.local_character_id IN (
    'e6bc06bf-75c2-4108-bb13-d84c477520e0',
    '90b7b7c3-ecaa-463d-9f12-ac87bd9fc375'
)
ORDER BY c.id;

-- 2. Direct guild membership lookup for BOTH remote IDs and BOTH local IDs.
-- A correctly linked membership should reference the Knight REMOTE ID.
SELECT
    gm.guild_id,
    g.name AS guild_name,
    gm.character_id,
    gm.role,
    to_jsonb(gm) AS membership_record
FROM public.guild_members AS gm
LEFT JOIN public.guilds AS g ON g.id = gm.guild_id
WHERE gm.character_id::text IN (
    '3b25c2d5-d3e3-4c02-9c8f-d7b08f156b0e',
    '3b39b880-cf5d-418f-af1e-c22fd6e9995b',
    'e6bc06bf-75c2-4108-bb13-d84c477520e0',
    '90b7b7c3-ecaa-463d-9f12-ac87bd9fc375'
)
ORDER BY gm.guild_id, gm.character_id;

-- 3. If either character has a membership, show the FULL roster of those
-- guilds. This helps detect a membership under an unexpected character ID.
SELECT
    gm.guild_id,
    g.name AS guild_name,
    gm.character_id,
    c.display_name,
    c.local_character_id,
    gm.role,
    to_jsonb(gm) AS membership_record
FROM public.guild_members AS gm
LEFT JOIN public.guilds AS g ON g.id = gm.guild_id
LEFT JOIN public.characters AS c ON c.id = gm.character_id
WHERE gm.guild_id IN (
    SELECT gm2.guild_id
    FROM public.guild_members AS gm2
    WHERE gm2.character_id::text IN (
        '3b25c2d5-d3e3-4c02-9c8f-d7b08f156b0e',
        '3b39b880-cf5d-418f-af1e-c22fd6e9995b',
        'e6bc06bf-75c2-4108-bb13-d84c477520e0',
        '90b7b7c3-ecaa-463d-9f12-ac87bd9fc375'
    )
)
ORDER BY gm.guild_id, gm.role, gm.character_id;

-- 4. Enumerate EVERY foreign key in public that references public.characters,
-- including the ON DELETE rule. This is the authoritative cascade/blocker list.
SELECT
    con.conname AS foreign_key_name,
    child_ns.nspname AS child_schema,
    child.relname AS child_table,
    child_col.attname AS child_column,
    parent_col.attname AS referenced_column,
    CASE con.confdeltype
        WHEN 'a' THEN 'NO ACTION'
        WHEN 'r' THEN 'RESTRICT'
        WHEN 'c' THEN 'CASCADE'
        WHEN 'n' THEN 'SET NULL'
        WHEN 'd' THEN 'SET DEFAULT'
        ELSE con.confdeltype::text
    END AS on_delete,
    pg_get_constraintdef(con.oid) AS definition
FROM pg_constraint AS con
JOIN pg_class AS child ON child.oid = con.conrelid
JOIN pg_namespace AS child_ns ON child_ns.oid = child.relnamespace
JOIN pg_class AS parent ON parent.oid = con.confrelid
JOIN pg_namespace AS parent_ns ON parent_ns.oid = parent.relnamespace
JOIN LATERAL unnest(con.conkey) WITH ORDINALITY AS child_key(attnum, ord) ON true
JOIN LATERAL unnest(con.confkey) WITH ORDINALITY AS parent_key(attnum, ord)
    ON parent_key.ord = child_key.ord
JOIN pg_attribute AS child_col
    ON child_col.attrelid = child.oid AND child_col.attnum = child_key.attnum
JOIN pg_attribute AS parent_col
    ON parent_col.attrelid = parent.oid AND parent_col.attnum = parent_key.attnum
WHERE con.contype = 'f'
  AND parent_ns.nspname = 'public'
  AND parent.relname = 'characters'
ORDER BY child_ns.nspname, child.relname, con.conname, child_key.ord;

-- 5. Generate read-only row-inspection SELECT statements for every FK column
-- that references characters. Copy the generated statements from the result
-- grid and run them to see the actual affected rows for Knight and Mage.
SELECT DISTINCT
    format(
        'SELECT %L AS source_table, to_jsonb(t) AS row_data FROM %I.%I AS t WHERE %I::text IN (%L, %L, %L, %L) ORDER BY 1 LIMIT 200;',
        child_ns.nspname || '.' || child.relname || '.' || child_col.attname,
        child_ns.nspname,
        child.relname,
        child_col.attname,
        '3b25c2d5-d3e3-4c02-9c8f-d7b08f156b0e',
        '3b39b880-cf5d-418f-af1e-c22fd6e9995b',
        'e6bc06bf-75c2-4108-bb13-d84c477520e0',
        '90b7b7c3-ecaa-463d-9f12-ac87bd9fc375'
    ) AS generated_read_only_query
FROM pg_constraint AS con
JOIN pg_class AS child ON child.oid = con.conrelid
JOIN pg_namespace AS child_ns ON child_ns.oid = child.relnamespace
JOIN pg_class AS parent ON parent.oid = con.confrelid
JOIN LATERAL unnest(con.conkey) WITH ORDINALITY AS child_key(attnum, ord) ON true
JOIN pg_attribute AS child_col
    ON child_col.attrelid = child.oid AND child_col.attnum = child_key.attnum
WHERE con.contype = 'f'
  AND child_ns.nspname = 'public'
  AND parent.relnamespace = 'public'::regnamespace
  AND parent.relname = 'characters'
ORDER BY 1;

-- 6. Find likely character-reference columns that do NOT have a declared
-- foreign key. These can include guild/chat/history tables whose ownership
-- is enforced by application logic rather than a database FK.
SELECT
    cols.table_schema,
    cols.table_name,
    cols.column_name,
    cols.data_type,
    cols.udt_name
FROM information_schema.columns AS cols
WHERE cols.table_schema = 'public'
  AND (
      cols.column_name ILIKE '%character%id%'
      OR cols.column_name ILIKE '%owner%id%'
      OR cols.column_name ILIKE '%founder%id%'
      OR cols.column_name ILIKE '%member%id%'
  )
  AND NOT EXISTS (
      SELECT 1
      FROM information_schema.key_column_usage AS kcu
      JOIN information_schema.table_constraints AS tc
        ON tc.constraint_name = kcu.constraint_name
       AND tc.constraint_schema = kcu.constraint_schema
       AND tc.table_schema = kcu.table_schema
       AND tc.table_name = kcu.table_name
      WHERE tc.constraint_type = 'FOREIGN KEY'
        AND kcu.table_schema = cols.table_schema
        AND kcu.table_name = cols.table_name
        AND kcu.column_name = cols.column_name
  )
ORDER BY cols.table_name, cols.ordinal_position;

-- 7. Inspect DELETE triggers on public.characters. This reveals trigger-based
-- cleanup or side effects not visible in the FK list.
SELECT
    trigger_name,
    event_manipulation,
    action_timing,
    action_statement
FROM information_schema.triggers
WHERE event_object_schema = 'public'
  AND event_object_table = 'characters'
  AND event_manipulation = 'DELETE'
ORDER BY trigger_name;

-- 8. Show RLS status and policies on guild and character-linked tables.
SELECT
    tablename,
    rowsecurity AS rls_enabled
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename IN (
      'characters',
      'guilds',
      'guild_members',
      'guild_events',
      'guild_leader_votes',
      'guild_leader_vote_ballots'
  )
ORDER BY tablename;

SELECT
    tablename,
    policyname,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE schemaname = 'public'
  AND tablename IN (
      'characters',
      'guilds',
      'guild_members',
      'guild_events',
      'guild_leader_votes',
      'guild_leader_vote_ballots'
  )
ORDER BY tablename, policyname;
