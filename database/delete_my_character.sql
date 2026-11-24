-- Review-only SQL for deleting the one confirmed incorrect Venilla Mage.
-- This function is intentionally restricted to the exact Mage IDs. It cannot
-- be used to delete the Knight or any other character.
--
-- No SQL is executed by this file being committed to GitHub.
--
-- Deleting public.characters cascades only through the existing
-- character_saves and character_skill_levels foreign keys. Other character-
-- linked records were audited separately and must remain zero for this ID.

CREATE OR REPLACE FUNCTION public.delete_my_character(p_character_id uuid)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $function$
DECLARE
    v_profile_id uuid;
    v_character_count bigint;
BEGIN
    v_profile_id := auth.uid();

    IF v_profile_id IS NULL THEN
        RAISE EXCEPTION 'Authentication is required.';
    END IF;

    -- Serialize deletions for this profile so two requests cannot both pass
    -- the last-character check at the same time.
    PERFORM pg_advisory_xact_lock(hashtext(v_profile_id::text));

    -- Fail closed unless both identifiers match the exact incorrect Mage.
    IF p_character_id IS DISTINCT FROM
        '3b39b880-cf5d-418f-af1e-c22fd6e9995b'::uuid THEN
        RAISE EXCEPTION 'This deletion is restricted to the confirmed incorrect Mage.';
    END IF;

    PERFORM 1
    FROM public.characters AS c
    WHERE c.id = p_character_id
      AND c.local_character_id = '90b7b7c3-ecaa-463d-9f12-ac87bd9fc375'
      AND c.profile_id = v_profile_id
    FOR UPDATE;

    IF NOT FOUND THEN
        RETURN false;
    END IF;

    SELECT count(*)
    INTO v_character_count
    FROM public.characters AS c
    WHERE c.profile_id = v_profile_id;

    IF v_character_count <= 1 THEN
        RAISE EXCEPTION 'The last character cannot be deleted.';
    END IF;

    DELETE FROM public.characters AS c
    WHERE c.id = p_character_id
      AND c.local_character_id = '90b7b7c3-ecaa-463d-9f12-ac87bd9fc375'
      AND c.profile_id = v_profile_id;

    RETURN FOUND;
END;
$function$;

REVOKE ALL ON FUNCTION public.delete_my_character(uuid) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.delete_my_character(uuid) TO authenticated;
