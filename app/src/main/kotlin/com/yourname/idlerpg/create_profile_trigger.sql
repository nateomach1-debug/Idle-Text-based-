-- Auto-create a profiles row whenever a new auth.users row appears.
-- Username is derived from the email's local part since nothing else
-- is available at signup time (the app doesn't currently pass a
-- username via signUpWith's metadata - worth adding later so this
-- can use the real chosen username instead of guessing from email).

create or replace function public.handle_new_auth_user()
returns trigger
language plpgsql
security definer
as $$
begin
    insert into public.profiles (id, username, created_at, free_guild_creation_used, is_moderator)
    values (
        new.id,
        split_part(new.email, '@', 1),
        now(),
        false,
        false
    )
    on conflict (id) do nothing;
    return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
    after insert on auth.users
    for each row execute function public.handle_new_auth_user();

-- One-time backfill for the account that already exists in auth.users
-- from before this trigger was created.
insert into public.profiles (id, username, created_at, free_guild_creation_used, is_moderator)
values (
    '4453e95f-80e0-4aa3-b62f-479acdafa6a7',
    'nateomach1',
    now(),
    false,
    true
)
on conflict (id) do nothing;
