-- ================================================================
-- FREESTYLEDB USER DATA SQL DUMP
-- Generated: October 11, 2025 23:16:36 EST
-- Database: PostgreSQL (Supabase)
-- Schema: public
-- Tables: profiles, user_closet, fit_feedback
-- ================================================================
--
-- This dump contains user-specific data including:
-- - User profiles (extends auth.users)
-- - User closets (owned product variants)
-- - Fit feedback (try-on experiences)
--
-- Note: These tables have Row Level Security (RLS) enabled
-- Users can only access their own data via RLS policies
--
-- ================================================================

BEGIN;

-- ================================================================
-- TABLE STRUCTURES
-- ================================================================

-- PROFILES
-- Extends Supabase auth.users with additional profile data
CREATE TABLE IF NOT EXISTS profiles (
  user_id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  display_name text,
  avatar_url text,
  created_at timestamptz NOT NULL DEFAULT now()
);

-- USER_CLOSET  
-- Tracks which products (variants) a user owns
CREATE TABLE IF NOT EXISTS user_closet (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  variant_id bigint NOT NULL REFERENCES variant(id),
  size text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  env text NOT NULL DEFAULT 'prod'  -- 'prod' or 'sandbox'
);

CREATE INDEX IF NOT EXISTS idx_closet_user_env ON user_closet(user_id, env);
CREATE INDEX IF NOT EXISTS idx_closet_variant_size ON user_closet(variant_id, size);

-- FIT_FEEDBACK
-- User try-on logs and fit votes
CREATE TABLE IF NOT EXISTS fit_feedback (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  variant_id bigint NOT NULL REFERENCES variant(id),
  tried_size text NOT NULL,
  fit_result smallint NOT NULL,  -- -1 = too small, 0 = perfect, +1 = too large
  notes text,
  created_at timestamptz NOT NULL DEFAULT now(),
  env text NOT NULL DEFAULT 'prod'
);

CREATE INDEX IF NOT EXISTS idx_fit_user_env ON fit_feedback(user_id, env);

-- ================================================================
-- ROW LEVEL SECURITY
-- ================================================================

-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_closet ENABLE ROW LEVEL SECURITY;
ALTER TABLE fit_feedback ENABLE ROW LEVEL SECURITY;

-- RLS Policies: users can only access their own data
DROP POLICY IF EXISTS profiles_self ON profiles;
CREATE POLICY profiles_self ON profiles
  FOR ALL USING (user_id = auth.uid()) 
  WITH CHECK (user_id = auth.uid());

DROP POLICY IF EXISTS closet_self ON user_closet;
CREATE POLICY closet_self ON user_closet
  FOR ALL USING (user_id = auth.uid()) 
  WITH CHECK (user_id = auth.uid());

DROP POLICY IF EXISTS fit_self ON fit_feedback;
CREATE POLICY fit_self ON fit_feedback
  FOR ALL USING (user_id = auth.uid()) 
  WITH CHECK (user_id = auth.uid());

-- ================================================================
-- RPC FUNCTIONS
-- ================================================================

-- FEED_PROXIES_SANDBOX
-- Server-side function to find "size twins" (other sandbox users with matching variant+size)
CREATE OR REPLACE FUNCTION feed_proxies_sandbox()
RETURNS TABLE(
  proxy_user_id uuid,
  variant_id bigint,
  size text
)
LANGUAGE sql
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT 
    uc2.user_id as proxy_user_id, 
    uc2.variant_id, 
    uc2.size
  FROM user_closet uc1
  JOIN user_closet uc2
    ON uc2.variant_id = uc1.variant_id
   AND uc2.size = uc1.size
   AND uc2.user_id <> uc1.user_id
   AND uc2.env = 'sandbox'
  WHERE uc1.user_id = auth.uid()
    AND uc1.env = 'sandbox';
$$;

-- RESET_DEMO_USER
-- Idempotent function to reset a user's sandbox data (for repeatable demos)
CREATE OR REPLACE FUNCTION reset_demo_user(
  seed_variant_id bigint DEFAULT NULL, 
  seed_size text DEFAULT NULL
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  me uuid := auth.uid();
BEGIN
  -- Clear existing sandbox data for this user
  DELETE FROM fit_feedback WHERE user_id = me AND env = 'sandbox';
  DELETE FROM user_closet WHERE user_id = me AND env = 'sandbox';

  -- Optionally seed with one closet item for instant feed population
  IF seed_variant_id IS NOT NULL THEN
    INSERT INTO user_closet(user_id, variant_id, size, env)
    VALUES (me, seed_variant_id, COALESCE(seed_size, 'M'), 'sandbox');
  END IF;
END;
$$;

SET

-- PROFILES DATA
             header             
--------------------------------
 -- No profile data (0 records)
(1 row)

 insert_stmt 
-------------
(0 rows)


-- USER_CLOSET DATA
            header             
-------------------------------
 -- No closet data (0 records)
(1 row)

 insert_stmt 
-------------
(0 rows)


-- FIT_FEEDBACK DATA
               header                
-------------------------------------
 -- No fit feedback data (0 records)
(1 row)

 insert_stmt 
-------------
(0 rows)


-- ================================================================
-- STATISTICS
-- ================================================================

COMMIT;

-- ================================================================
-- SUMMARY
-- ================================================================

-- Dump completed successfully
-- Date: October 11, 2025 23:16:36 EST
-- 
-- Current Statistics:
-- - User Profiles: 0 records
-- - Closet Items: 0 records
-- - Fit Feedback: 0 records
--
-- Notes:
-- 1. All tables have Row Level Security (RLS) enabled
-- 2. Users can only access their own data via auth.uid()
-- 3. The 'env' column allows separation of 'prod' vs 'sandbox' data
-- 4. Sandbox data enables repeatable demos without affecting production
-- 5. RPC functions provide safe cross-user queries (e.g., finding size twins)
--
-- Usage Examples:
--
-- 1. Reset demo user (clear sandbox data):
--    SELECT reset_demo_user(20, 'M');
--
-- 2. Add item to closet:
--    INSERT INTO user_closet (user_id, variant_id, size, env)
--    VALUES (auth.uid(), 21, 'L', 'sandbox');
--
-- 3. Add fit feedback:
--    INSERT INTO fit_feedback (user_id, variant_id, tried_size, fit_result, env)
--    VALUES (auth.uid(), 21, 'L', 0, 'sandbox');
--
-- 4. Find size twins:
--    SELECT * FROM feed_proxies_sandbox();
--
-- ================================================================

