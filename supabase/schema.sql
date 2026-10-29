-- ==============================================================================
-- LOKĀNTRA - Supabase Authentication & User Login Tracking Schema
-- ==============================================================================
-- Run this script in your Supabase SQL Editor:
-- Dashboard -> SQL Editor -> New Query -> Paste & Run
-- ==============================================================================

-- 1. Create profiles table (holds user profile data synced from Google / Auth)
CREATE TABLE IF NOT EXISTS public.profiles (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email TEXT,
  full_name TEXT,
  avatar_url TEXT,
  provider TEXT DEFAULT 'google',
  created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
  updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
  last_sign_in_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now())
);

-- Enable RLS on profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Profiles RLS Policies
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
CREATE POLICY "Users can view own profile"
  ON public.profiles FOR SELECT
  USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile"
  ON public.profiles FOR UPDATE
  USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can insert own profile" ON public.profiles;
CREATE POLICY "Users can insert own profile"
  ON public.profiles FOR INSERT
  WITH CHECK (auth.uid() = id);

-- 2. Create login_history table (records every login event with timestamps & metadata)
CREATE TABLE IF NOT EXISTS public.login_history (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  email TEXT,
  provider TEXT DEFAULT 'google',
  logged_in_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
  user_agent TEXT,
  metadata JSONB DEFAULT '{}'::jsonb
);

-- Enable RLS on login_history
ALTER TABLE public.login_history ENABLE ROW LEVEL SECURITY;

-- Login History RLS Policies
DROP POLICY IF EXISTS "Users can view own login history" ON public.login_history;
CREATE POLICY "Users can view own login history"
  ON public.login_history FOR SELECT
  USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can insert own login history" ON public.login_history;
CREATE POLICY "Users can insert own login history"
  ON public.login_history FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- 3. Automatic Trigger Function: Sync auth.users to public.profiles and log login events
CREATE OR REPLACE FUNCTION public.handle_user_auth_event()
RETURNS TRIGGER AS $$
DECLARE
  extracted_name TEXT;
  extracted_avatar TEXT;
  auth_provider TEXT;
BEGIN
  -- Extract name from metadata (Google provides 'name' or 'full_name')
  extracted_name := COALESCE(
    NEW.raw_user_meta_data->>'full_name',
    NEW.raw_user_meta_data->>'name',
    split_part(NEW.email, '@', 1)
  );

  -- Extract avatar URL from metadata (Google provides 'avatar_url' or 'picture')
  extracted_avatar := COALESCE(
    NEW.raw_user_meta_data->>'avatar_url',
    NEW.raw_user_meta_data->>'picture',
    ''
  );

  -- Extract provider
  auth_provider := COALESCE(
    NEW.raw_app_meta_data->>'provider',
    'google'
  );

  -- 1) Upsert into public.profiles
  INSERT INTO public.profiles (
    id,
    email,
    full_name,
    avatar_url,
    provider,
    updated_at,
    last_sign_in_at
  )
  VALUES (
    NEW.id,
    NEW.email,
    extracted_name,
    extracted_avatar,
    auth_provider,
    timezone('utc'::text, now()),
    COALESCE(NEW.last_sign_in_at, timezone('utc'::text, now()))
  )
  ON CONFLICT (id) DO UPDATE SET
    email = EXCLUDED.email,
    full_name = COALESCE(EXCLUDED.full_name, profiles.full_name),
    avatar_url = COALESCE(EXCLUDED.avatar_url, profiles.avatar_url),
    provider = EXCLUDED.provider,
    updated_at = timezone('utc'::text, now()),
    last_sign_in_at = COALESCE(NEW.last_sign_in_at, timezone('utc'::text, now()));

  -- 2) Record entry in login_history
  INSERT INTO public.login_history (
    user_id,
    email,
    provider,
    logged_in_at,
    metadata
  )
  VALUES (
    NEW.id,
    NEW.email,
    auth_provider,
    COALESCE(NEW.last_sign_in_at, timezone('utc'::text, now())),
    jsonb_build_object(
      'raw_user_meta_data', NEW.raw_user_meta_data,
      'app_metadata', NEW.raw_app_meta_data
    )
  );

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 4. Create trigger on auth.users for signup and signin events
DROP TRIGGER IF EXISTS on_auth_user_created_or_updated ON auth.users;
CREATE TRIGGER on_auth_user_created_or_updated
  AFTER INSERT OR UPDATE OF last_sign_in_at ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_user_auth_event();

-- Index for fast queries on login history by user
CREATE INDEX IF NOT EXISTS idx_login_history_user_id ON public.login_history(user_id);
CREATE INDEX IF NOT EXISTS idx_login_history_logged_in_at ON public.login_history(logged_in_at DESC);
