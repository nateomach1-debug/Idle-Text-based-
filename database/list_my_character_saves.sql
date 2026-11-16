-- Read-only metadata lookup for every character/save owned by the
-- currently authenticated Supabase profile.
--
-- This intentionally accepts no profile ID parameter: auth.uid() is the
-- only source of ownership. It returns metadata only, never save_data.
-- LEFT JOIN keeps registered characters visible even if they have no save.

CREATE OR REPLACE FUNCTION public.list_my_character_saves()
RETURNS TABLE (
    supabase_character_id uuid,
    local_character_id text,
    display_name text,
    created_at timestamp with time zone,
    save_updated_at timestamp with time zone
)
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $function$
    SELECT
        c.id,
        c.local_character_id,
        c.display_name,
        c.created_at,
        s.updated_at
    FROM public.characters AS c
    LEFT JOIN public.character_saves AS s
        ON s.character_id = c.id
    WHERE c.profile_id = auth.uid()
    ORDER BY c.created_at ASC, c.id ASC;
$function$;

REVOKE ALL ON FUNCTION public.list_my_character_saves() FROM PUBLIC;
GRANT EXECUTE ON FUNCTION public.list_my_character_saves() TO authenticated;
