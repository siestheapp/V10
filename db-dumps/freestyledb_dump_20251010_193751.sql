--
-- PostgreSQL database dump
--

\restrict oqEaczop9hctEKCKmaJeIRhcIdTd1FdgE46ERXivFUbwFlXPqJpbJWvJctskrq7

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6 (Homebrew)

-- Started on 2025-10-10 19:37:51 EDT

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 38 (class 2615 OID 16494)
-- Name: auth; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA "auth";


--
-- TOC entry 24 (class 2615 OID 16388)
-- Name: extensions; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA "extensions";


--
-- TOC entry 36 (class 2615 OID 16624)
-- Name: graphql; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA "graphql";


--
-- TOC entry 35 (class 2615 OID 16613)
-- Name: graphql_public; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA "graphql_public";


--
-- TOC entry 7 (class 3079 OID 23364)
-- Name: pg_net; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "pg_net" WITH SCHEMA "extensions";


--
-- TOC entry 4409 (class 0 OID 0)
-- Dependencies: 7
-- Name: EXTENSION "pg_net"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION "pg_net" IS 'Async HTTP';


--
-- TOC entry 13 (class 2615 OID 16386)
-- Name: pgbouncer; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA "pgbouncer";


--
-- TOC entry 4410 (class 0 OID 0)
-- Dependencies: 14
-- Name: SCHEMA "public"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA "public" IS 'standard public schema';


--
-- TOC entry 10 (class 2615 OID 16605)
-- Name: realtime; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA "realtime";


--
-- TOC entry 39 (class 2615 OID 16542)
-- Name: storage; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA "storage";


--
-- TOC entry 109 (class 2615 OID 23409)
-- Name: supabase_functions; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA "supabase_functions";


--
-- TOC entry 33 (class 2615 OID 16653)
-- Name: vault; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA "vault";


--
-- TOC entry 6 (class 3079 OID 16689)
-- Name: pg_graphql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "pg_graphql" WITH SCHEMA "graphql";


--
-- TOC entry 4411 (class 0 OID 0)
-- Dependencies: 6
-- Name: EXTENSION "pg_graphql"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION "pg_graphql" IS 'pg_graphql: GraphQL support';


--
-- TOC entry 2 (class 3079 OID 16389)
-- Name: pg_stat_statements; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";


--
-- TOC entry 4412 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION "pg_stat_statements"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION "pg_stat_statements" IS 'track planning and execution statistics of all SQL statements executed';


--
-- TOC entry 4 (class 3079 OID 16443)
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";


--
-- TOC entry 4413 (class 0 OID 0)
-- Dependencies: 4
-- Name: EXTENSION "pgcrypto"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION "pgcrypto" IS 'cryptographic functions';


--
-- TOC entry 5 (class 3079 OID 16654)
-- Name: supabase_vault; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "supabase_vault" WITH SCHEMA "vault";


--
-- TOC entry 4414 (class 0 OID 0)
-- Dependencies: 5
-- Name: EXTENSION "supabase_vault"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION "supabase_vault" IS 'Supabase Vault Extension';


--
-- TOC entry 3 (class 3079 OID 16432)
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "extensions";


--
-- TOC entry 4415 (class 0 OID 0)
-- Dependencies: 3
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- TOC entry 1214 (class 1247 OID 16782)
-- Name: aal_level; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE "auth"."aal_level" AS ENUM (
    'aal1',
    'aal2',
    'aal3'
);


--
-- TOC entry 1238 (class 1247 OID 16923)
-- Name: code_challenge_method; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE "auth"."code_challenge_method" AS ENUM (
    's256',
    'plain'
);


--
-- TOC entry 1211 (class 1247 OID 16776)
-- Name: factor_status; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE "auth"."factor_status" AS ENUM (
    'unverified',
    'verified'
);


--
-- TOC entry 1208 (class 1247 OID 16771)
-- Name: factor_type; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE "auth"."factor_type" AS ENUM (
    'totp',
    'webauthn',
    'phone'
);


--
-- TOC entry 1250 (class 1247 OID 17004)
-- Name: oauth_registration_type; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE "auth"."oauth_registration_type" AS ENUM (
    'dynamic',
    'manual'
);


--
-- TOC entry 1244 (class 1247 OID 16965)
-- Name: one_time_token_type; Type: TYPE; Schema: auth; Owner: -
--

CREATE TYPE "auth"."one_time_token_type" AS ENUM (
    'confirmation_token',
    'reauthentication_token',
    'recovery_token',
    'email_change_token_new',
    'email_change_token_current',
    'phone_change_token'
);


--
-- TOC entry 1263 (class 1247 OID 17158)
-- Name: action; Type: TYPE; Schema: realtime; Owner: -
--

CREATE TYPE "realtime"."action" AS ENUM (
    'INSERT',
    'UPDATE',
    'DELETE',
    'TRUNCATE',
    'ERROR'
);


--
-- TOC entry 1268 (class 1247 OID 17115)
-- Name: equality_op; Type: TYPE; Schema: realtime; Owner: -
--

CREATE TYPE "realtime"."equality_op" AS ENUM (
    'eq',
    'neq',
    'lt',
    'lte',
    'gt',
    'gte',
    'in'
);


--
-- TOC entry 1271 (class 1247 OID 17129)
-- Name: user_defined_filter; Type: TYPE; Schema: realtime; Owner: -
--

CREATE TYPE "realtime"."user_defined_filter" AS (
	"column_name" "text",
	"op" "realtime"."equality_op",
	"value" "text"
);


--
-- TOC entry 1280 (class 1247 OID 17200)
-- Name: wal_column; Type: TYPE; Schema: realtime; Owner: -
--

CREATE TYPE "realtime"."wal_column" AS (
	"name" "text",
	"type_name" "text",
	"type_oid" "oid",
	"value" "jsonb",
	"is_pkey" boolean,
	"is_selectable" boolean
);


--
-- TOC entry 1277 (class 1247 OID 17171)
-- Name: wal_rls; Type: TYPE; Schema: realtime; Owner: -
--

CREATE TYPE "realtime"."wal_rls" AS (
	"wal" "jsonb",
	"is_rls_enabled" boolean,
	"subscription_ids" "uuid"[],
	"errors" "text"[]
);


--
-- TOC entry 1388 (class 1247 OID 43337)
-- Name: buckettype; Type: TYPE; Schema: storage; Owner: -
--

CREATE TYPE "storage"."buckettype" AS ENUM (
    'STANDARD',
    'ANALYTICS'
);


--
-- TOC entry 467 (class 1255 OID 16540)
-- Name: email(); Type: FUNCTION; Schema: auth; Owner: -
--

CREATE FUNCTION "auth"."email"() RETURNS "text"
    LANGUAGE "sql" STABLE
    AS $$
  select 
  coalesce(
    nullif(current_setting('request.jwt.claim.email', true), ''),
    (nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'email')
  )::text
$$;


--
-- TOC entry 4416 (class 0 OID 0)
-- Dependencies: 467
-- Name: FUNCTION "email"(); Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON FUNCTION "auth"."email"() IS 'Deprecated. Use auth.jwt() -> ''email'' instead.';


--
-- TOC entry 487 (class 1255 OID 16753)
-- Name: jwt(); Type: FUNCTION; Schema: auth; Owner: -
--

CREATE FUNCTION "auth"."jwt"() RETURNS "jsonb"
    LANGUAGE "sql" STABLE
    AS $$
  select 
    coalesce(
        nullif(current_setting('request.jwt.claim', true), ''),
        nullif(current_setting('request.jwt.claims', true), '')
    )::jsonb
$$;


--
-- TOC entry 422 (class 1255 OID 16539)
-- Name: role(); Type: FUNCTION; Schema: auth; Owner: -
--

CREATE FUNCTION "auth"."role"() RETURNS "text"
    LANGUAGE "sql" STABLE
    AS $$
  select 
  coalesce(
    nullif(current_setting('request.jwt.claim.role', true), ''),
    (nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'role')
  )::text
$$;


--
-- TOC entry 4417 (class 0 OID 0)
-- Dependencies: 422
-- Name: FUNCTION "role"(); Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON FUNCTION "auth"."role"() IS 'Deprecated. Use auth.jwt() -> ''role'' instead.';


--
-- TOC entry 442 (class 1255 OID 16538)
-- Name: uid(); Type: FUNCTION; Schema: auth; Owner: -
--

CREATE FUNCTION "auth"."uid"() RETURNS "uuid"
    LANGUAGE "sql" STABLE
    AS $$
  select 
  coalesce(
    nullif(current_setting('request.jwt.claim.sub', true), ''),
    (nullif(current_setting('request.jwt.claims', true), '')::jsonb ->> 'sub')
  )::uuid
$$;


--
-- TOC entry 4418 (class 0 OID 0)
-- Dependencies: 442
-- Name: FUNCTION "uid"(); Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON FUNCTION "auth"."uid"() IS 'Deprecated. Use auth.jwt() -> ''sub'' instead.';


--
-- TOC entry 504 (class 1255 OID 16597)
-- Name: grant_pg_cron_access(); Type: FUNCTION; Schema: extensions; Owner: -
--

CREATE FUNCTION "extensions"."grant_pg_cron_access"() RETURNS "event_trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
  IF EXISTS (
    SELECT
    FROM pg_event_trigger_ddl_commands() AS ev
    JOIN pg_extension AS ext
    ON ev.objid = ext.oid
    WHERE ext.extname = 'pg_cron'
  )
  THEN
    grant usage on schema cron to postgres with grant option;

    alter default privileges in schema cron grant all on tables to postgres with grant option;
    alter default privileges in schema cron grant all on functions to postgres with grant option;
    alter default privileges in schema cron grant all on sequences to postgres with grant option;

    alter default privileges for user supabase_admin in schema cron grant all
        on sequences to postgres with grant option;
    alter default privileges for user supabase_admin in schema cron grant all
        on tables to postgres with grant option;
    alter default privileges for user supabase_admin in schema cron grant all
        on functions to postgres with grant option;

    grant all privileges on all tables in schema cron to postgres with grant option;
    revoke all on table cron.job from postgres;
    grant select on table cron.job to postgres with grant option;
  END IF;
END;
$$;


--
-- TOC entry 4419 (class 0 OID 0)
-- Dependencies: 504
-- Name: FUNCTION "grant_pg_cron_access"(); Type: COMMENT; Schema: extensions; Owner: -
--

COMMENT ON FUNCTION "extensions"."grant_pg_cron_access"() IS 'Grants access to pg_cron';


--
-- TOC entry 482 (class 1255 OID 16618)
-- Name: grant_pg_graphql_access(); Type: FUNCTION; Schema: extensions; Owner: -
--

CREATE FUNCTION "extensions"."grant_pg_graphql_access"() RETURNS "event_trigger"
    LANGUAGE "plpgsql"
    AS $_$
DECLARE
    func_is_graphql_resolve bool;
BEGIN
    func_is_graphql_resolve = (
        SELECT n.proname = 'resolve'
        FROM pg_event_trigger_ddl_commands() AS ev
        LEFT JOIN pg_catalog.pg_proc AS n
        ON ev.objid = n.oid
    );

    IF func_is_graphql_resolve
    THEN
        -- Update public wrapper to pass all arguments through to the pg_graphql resolve func
        DROP FUNCTION IF EXISTS graphql_public.graphql;
        create or replace function graphql_public.graphql(
            "operationName" text default null,
            query text default null,
            variables jsonb default null,
            extensions jsonb default null
        )
            returns jsonb
            language sql
        as $$
            select graphql.resolve(
                query := query,
                variables := coalesce(variables, '{}'),
                "operationName" := "operationName",
                extensions := extensions
            );
        $$;

        -- This hook executes when `graphql.resolve` is created. That is not necessarily the last
        -- function in the extension so we need to grant permissions on existing entities AND
        -- update default permissions to any others that are created after `graphql.resolve`
        grant usage on schema graphql to postgres, anon, authenticated, service_role;
        grant select on all tables in schema graphql to postgres, anon, authenticated, service_role;
        grant execute on all functions in schema graphql to postgres, anon, authenticated, service_role;
        grant all on all sequences in schema graphql to postgres, anon, authenticated, service_role;
        alter default privileges in schema graphql grant all on tables to postgres, anon, authenticated, service_role;
        alter default privileges in schema graphql grant all on functions to postgres, anon, authenticated, service_role;
        alter default privileges in schema graphql grant all on sequences to postgres, anon, authenticated, service_role;

        -- Allow postgres role to allow granting usage on graphql and graphql_public schemas to custom roles
        grant usage on schema graphql_public to postgres with grant option;
        grant usage on schema graphql to postgres with grant option;
    END IF;

END;
$_$;


--
-- TOC entry 4420 (class 0 OID 0)
-- Dependencies: 482
-- Name: FUNCTION "grant_pg_graphql_access"(); Type: COMMENT; Schema: extensions; Owner: -
--

COMMENT ON FUNCTION "extensions"."grant_pg_graphql_access"() IS 'Grants access to pg_graphql';


--
-- TOC entry 459 (class 1255 OID 16599)
-- Name: grant_pg_net_access(); Type: FUNCTION; Schema: extensions; Owner: -
--

CREATE FUNCTION "extensions"."grant_pg_net_access"() RETURNS "event_trigger"
    LANGUAGE "plpgsql"
    AS $$
  BEGIN
    IF EXISTS (
      SELECT 1
      FROM pg_event_trigger_ddl_commands() AS ev
      JOIN pg_extension AS ext
      ON ev.objid = ext.oid
      WHERE ext.extname = 'pg_net'
    )
    THEN
      GRANT USAGE ON SCHEMA net TO supabase_functions_admin, postgres, anon, authenticated, service_role;

      IF EXISTS (
        SELECT FROM pg_extension
        WHERE extname = 'pg_net'
        -- all versions in use on existing projects as of 2025-02-20
        -- version 0.12.0 onwards don't need these applied
        AND extversion IN ('0.2', '0.6', '0.7', '0.7.1', '0.8', '0.10.0', '0.11.0')
      ) THEN
        ALTER function net.http_get(url text, params jsonb, headers jsonb, timeout_milliseconds integer) SECURITY DEFINER;
        ALTER function net.http_post(url text, body jsonb, params jsonb, headers jsonb, timeout_milliseconds integer) SECURITY DEFINER;

        ALTER function net.http_get(url text, params jsonb, headers jsonb, timeout_milliseconds integer) SET search_path = net;
        ALTER function net.http_post(url text, body jsonb, params jsonb, headers jsonb, timeout_milliseconds integer) SET search_path = net;

        REVOKE ALL ON FUNCTION net.http_get(url text, params jsonb, headers jsonb, timeout_milliseconds integer) FROM PUBLIC;
        REVOKE ALL ON FUNCTION net.http_post(url text, body jsonb, params jsonb, headers jsonb, timeout_milliseconds integer) FROM PUBLIC;

        GRANT EXECUTE ON FUNCTION net.http_get(url text, params jsonb, headers jsonb, timeout_milliseconds integer) TO supabase_functions_admin, postgres, anon, authenticated, service_role;
        GRANT EXECUTE ON FUNCTION net.http_post(url text, body jsonb, params jsonb, headers jsonb, timeout_milliseconds integer) TO supabase_functions_admin, postgres, anon, authenticated, service_role;
      END IF;
    END IF;
  END;
  $$;


--
-- TOC entry 4421 (class 0 OID 0)
-- Dependencies: 459
-- Name: FUNCTION "grant_pg_net_access"(); Type: COMMENT; Schema: extensions; Owner: -
--

COMMENT ON FUNCTION "extensions"."grant_pg_net_access"() IS 'Grants access to pg_net';


--
-- TOC entry 415 (class 1255 OID 16609)
-- Name: pgrst_ddl_watch(); Type: FUNCTION; Schema: extensions; Owner: -
--

CREATE FUNCTION "extensions"."pgrst_ddl_watch"() RETURNS "event_trigger"
    LANGUAGE "plpgsql"
    AS $$
DECLARE
  cmd record;
BEGIN
  FOR cmd IN SELECT * FROM pg_event_trigger_ddl_commands()
  LOOP
    IF cmd.command_tag IN (
      'CREATE SCHEMA', 'ALTER SCHEMA'
    , 'CREATE TABLE', 'CREATE TABLE AS', 'SELECT INTO', 'ALTER TABLE'
    , 'CREATE FOREIGN TABLE', 'ALTER FOREIGN TABLE'
    , 'CREATE VIEW', 'ALTER VIEW'
    , 'CREATE MATERIALIZED VIEW', 'ALTER MATERIALIZED VIEW'
    , 'CREATE FUNCTION', 'ALTER FUNCTION'
    , 'CREATE TRIGGER'
    , 'CREATE TYPE', 'ALTER TYPE'
    , 'CREATE RULE'
    , 'COMMENT'
    )
    -- don't notify in case of CREATE TEMP table or other objects created on pg_temp
    AND cmd.schema_name is distinct from 'pg_temp'
    THEN
      NOTIFY pgrst, 'reload schema';
    END IF;
  END LOOP;
END; $$;


--
-- TOC entry 515 (class 1255 OID 16610)
-- Name: pgrst_drop_watch(); Type: FUNCTION; Schema: extensions; Owner: -
--

CREATE FUNCTION "extensions"."pgrst_drop_watch"() RETURNS "event_trigger"
    LANGUAGE "plpgsql"
    AS $$
DECLARE
  obj record;
BEGIN
  FOR obj IN SELECT * FROM pg_event_trigger_dropped_objects()
  LOOP
    IF obj.object_type IN (
      'schema'
    , 'table'
    , 'foreign table'
    , 'view'
    , 'materialized view'
    , 'function'
    , 'trigger'
    , 'type'
    , 'rule'
    )
    AND obj.is_temporary IS false -- no pg_temp objects
    THEN
      NOTIFY pgrst, 'reload schema';
    END IF;
  END LOOP;
END; $$;


--
-- TOC entry 428 (class 1255 OID 16620)
-- Name: set_graphql_placeholder(); Type: FUNCTION; Schema: extensions; Owner: -
--

CREATE FUNCTION "extensions"."set_graphql_placeholder"() RETURNS "event_trigger"
    LANGUAGE "plpgsql"
    AS $_$
    DECLARE
    graphql_is_dropped bool;
    BEGIN
    graphql_is_dropped = (
        SELECT ev.schema_name = 'graphql_public'
        FROM pg_event_trigger_dropped_objects() AS ev
        WHERE ev.schema_name = 'graphql_public'
    );

    IF graphql_is_dropped
    THEN
        create or replace function graphql_public.graphql(
            "operationName" text default null,
            query text default null,
            variables jsonb default null,
            extensions jsonb default null
        )
            returns jsonb
            language plpgsql
        as $$
            DECLARE
                server_version float;
            BEGIN
                server_version = (SELECT (SPLIT_PART((select version()), ' ', 2))::float);

                IF server_version >= 14 THEN
                    RETURN jsonb_build_object(
                        'errors', jsonb_build_array(
                            jsonb_build_object(
                                'message', 'pg_graphql extension is not enabled.'
                            )
                        )
                    );
                ELSE
                    RETURN jsonb_build_object(
                        'errors', jsonb_build_array(
                            jsonb_build_object(
                                'message', 'pg_graphql is only available on projects running Postgres 14 onwards.'
                            )
                        )
                    );
                END IF;
            END;
        $$;
    END IF;

    END;
$_$;


--
-- TOC entry 4422 (class 0 OID 0)
-- Dependencies: 428
-- Name: FUNCTION "set_graphql_placeholder"(); Type: COMMENT; Schema: extensions; Owner: -
--

COMMENT ON FUNCTION "extensions"."set_graphql_placeholder"() IS 'Reintroduces placeholder function for graphql_public.graphql';


--
-- TOC entry 469 (class 1255 OID 16387)
-- Name: get_auth("text"); Type: FUNCTION; Schema: pgbouncer; Owner: -
--

CREATE FUNCTION "pgbouncer"."get_auth"("p_usename" "text") RETURNS TABLE("username" "text", "password" "text")
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $_$
begin
    raise debug 'PgBouncer auth request: %', p_usename;

    return query
    select 
        rolname::text, 
        case when rolvaliduntil < now() 
            then null 
            else rolpassword::text 
        end 
    from pg_authid 
    where rolname=$1 and rolcanlogin;
end;
$_$;


--
-- TOC entry 503 (class 1255 OID 17990)
-- Name: upsert_variant("text", "text", "text", "text", "text", "text", "text", "text", "text", "text", "text", "text", "text", "text", "text", boolean, "text", numeric, numeric, "jsonb"); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION "public"."upsert_variant"("p_brand" "text", "p_category_slug" "text", "p_style_name" "text", "p_style_code" "text" DEFAULT NULL::"text", "p_style_code_type" "text" DEFAULT 'style_code'::"text", "p_gender" "text" DEFAULT NULL::"text", "p_variant_code" "text" DEFAULT NULL::"text", "p_variant_code_type" "text" DEFAULT 'sku'::"text", "p_code_region" "text" DEFAULT 'ALL'::"text", "p_color_original" "text" DEFAULT NULL::"text", "p_color_canonical" "text" DEFAULT NULL::"text", "p_fit" "text" DEFAULT NULL::"text", "p_fabric" "text" DEFAULT NULL::"text", "p_url" "text" DEFAULT NULL::"text", "p_url_region" "text" DEFAULT 'US'::"text", "p_is_variant_url" boolean DEFAULT true, "p_currency" "text" DEFAULT NULL::"text", "p_list" numeric DEFAULT NULL::numeric, "p_sale" numeric DEFAULT NULL::numeric, "p_attrs" "jsonb" DEFAULT '{}'::"jsonb") RETURNS bigint
    LANGUAGE "plpgsql" SECURITY DEFINER
    SET "search_path" TO 'public'
    AS $$
DECLARE
  v_brand_id    BIGINT;
  v_cat_id      BIGINT;
  v_style_id    BIGINT;
  v_style_code  TEXT := NULL;

  v_color_id    BIGINT;
  v_fit_id      BIGINT;
  v_fabric_id   BIGINT;

  v_variant_id  BIGINT;
  v_existing_id BIGINT;
BEGIN
  -- Brand
  INSERT INTO brand(name)
  VALUES (p_brand)
  ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
  RETURNING id INTO v_brand_id;

  -- Category
  INSERT INTO category(slug, name)
  VALUES (p_category_slug, initcap(p_category_slug))
  ON CONFLICT (slug) DO NOTHING;
  SELECT id INTO v_cat_id FROM category WHERE slug = p_category_slug;

  -- Style
  INSERT INTO style(brand_id, category_id, name, gender)
  VALUES (v_brand_id, v_cat_id, p_style_name, p_gender)
  ON CONFLICT (brand_id, name, category_id)
  DO UPDATE SET gender = COALESCE(EXCLUDED.gender, style.gender)
  RETURNING id INTO v_style_id;

  -- Style code (optional)
  IF p_style_code IS NOT NULL THEN
    INSERT INTO style_code(style_id, code, code_type, region)
    VALUES (v_style_id, p_style_code, COALESCE(p_style_code_type,'style_code'), 'ALL')
    ON CONFLICT (style_id, code, region) DO NOTHING;
    v_style_code := p_style_code;
  END IF;

  -- Color resolution
  IF p_color_canonical IS NOT NULL THEN
    INSERT INTO color_catalog(canonical)
    VALUES (p_color_canonical)
    ON CONFLICT (canonical) DO NOTHING;
    SELECT id INTO v_color_id FROM color_catalog WHERE canonical = p_color_canonical;

    IF p_color_original IS NOT NULL THEN
      INSERT INTO brand_color_map(brand_id, original, color_id)
      VALUES (v_brand_id, p_color_original, v_color_id)
      ON CONFLICT (brand_id, original) DO UPDATE SET color_id = EXCLUDED.color_id;
    END IF;

  ELSIF p_color_original IS NOT NULL THEN
    SELECT bcm.color_id INTO v_color_id
    FROM brand_color_map bcm
    WHERE bcm.brand_id = v_brand_id AND bcm.original = p_color_original;

    IF v_color_id IS NULL THEN
      INSERT INTO color_catalog(canonical)
      VALUES (p_color_original)
      ON CONFLICT (canonical) DO NOTHING;
      SELECT id INTO v_color_id FROM color_catalog WHERE canonical = p_color_original;

      INSERT INTO brand_color_map(brand_id, original, color_id)
      VALUES (v_brand_id, p_color_original, v_color_id)
      ON CONFLICT (brand_id, original) DO UPDATE SET color_id = EXCLUDED.color_id;
    END IF;
  END IF;

  -- Fit
  IF p_fit IS NOT NULL THEN
    INSERT INTO fit_catalog(name) VALUES (p_fit)
    ON CONFLICT (name) DO NOTHING;
    SELECT id INTO v_fit_id FROM fit_catalog WHERE name = p_fit;
  END IF;

  -- Fabric
  IF p_fabric IS NOT NULL THEN
    INSERT INTO fabric_catalog(name) VALUES (p_fabric)
    ON CONFLICT (name) DO NOTHING;
    SELECT id INTO v_fabric_id FROM fabric_catalog WHERE name = p_fabric;
  END IF;

  -- Variant identity: style + color + fit + fabric (NULL-safe)
  SELECT id INTO v_existing_id
  FROM variant
  WHERE style_id = v_style_id
    AND (color_id  IS NOT DISTINCT FROM v_color_id)
    AND (fit_id    IS NOT DISTINCT FROM v_fit_id)
    AND (fabric_id IS NOT DISTINCT FROM v_fabric_id)
  LIMIT 1;

  IF v_existing_id IS NULL THEN
    INSERT INTO variant(style_id, color_id, fit_id, fabric_id, attrs)
    VALUES (v_style_id, v_color_id, v_fit_id, v_fabric_id, COALESCE(p_attrs, '{}'::jsonb))
    RETURNING id INTO v_variant_id;
  ELSE
    v_variant_id := v_existing_id;
    IF p_attrs IS NOT NULL AND p_attrs <> '{}'::jsonb THEN
      UPDATE variant
      SET attrs = COALESCE(attrs, '{}'::jsonb) || p_attrs
      WHERE id = v_variant_id;
    END IF;
  END IF;

  -- Variant code
  IF p_variant_code IS NOT NULL THEN
    INSERT INTO variant_code(variant_id, code, code_type, region)
    VALUES (v_variant_id, p_variant_code, COALESCE(p_variant_code_type,'sku'), COALESCE(p_code_region,'ALL'))
    ON CONFLICT (variant_id, code, region) DO NOTHING;
  END IF;

  -- URL (variant or style)
  IF p_url IS NOT NULL THEN
    IF COALESCE(p_is_variant_url, TRUE) THEN
      INSERT INTO product_url(style_id, variant_id, region, url, is_current)
      VALUES (v_style_id, v_variant_id, COALESCE(p_url_region,'US'), p_url, TRUE)
      ON CONFLICT DO NOTHING;
    ELSE
      INSERT INTO product_url(style_id, variant_id, region, url, is_current)
      VALUES (v_style_id, NULL, COALESCE(p_url_region,'US'), p_url, TRUE)
      ON CONFLICT DO NOTHING;
    END IF;
  END IF;

  -- Price snapshot
  IF p_currency IS NOT NULL THEN
    INSERT INTO price_history(variant_id, region, currency, list_price, sale_price, captured_at)
    VALUES (v_variant_id, COALESCE(p_url_region,'US'), p_currency, p_list, p_sale, now())
    ON CONFLICT DO NOTHING;
  END IF;

  RETURN v_variant_id;
END;
$$;


--
-- TOC entry 445 (class 1255 OID 18620)
-- Name: upsert_variant_images("text", "text", "text"[], "text", "text", "text", "text", "text", "text"); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION "public"."upsert_variant_images"("p_brand" "text", "p_style_code" "text", "p_urls" "text"[] DEFAULT ARRAY[]::"text"[], "p_variant_code" "text" DEFAULT NULL::"text", "p_code_type" "text" DEFAULT NULL::"text", "p_region" "text" DEFAULT 'US'::"text", "p_primary_url" "text" DEFAULT NULL::"text", "p_color_code" "text" DEFAULT NULL::"text", "p_alt" "text" DEFAULT NULL::"text") RETURNS integer
    LANGUAGE "plpgsql" SECURITY DEFINER
    SET "search_path" TO 'public'
    AS $$
DECLARE
  v_style_id   BIGINT;
  v_variant_id BIGINT;
  v_count      INT := 0;
  l_url        TEXT;
BEGIN
  -- Resolve style by brand + style_code
  SELECT st.id INTO v_style_id
  FROM style st
  JOIN brand b ON b.id = st.brand_id AND b.name = p_brand
  JOIN style_code sc ON sc.style_id = st.id AND sc.code = p_style_code
  LIMIT 1;

  IF v_style_id IS NULL THEN
    RAISE EXCEPTION 'Style % / % not found', p_brand, p_style_code;
  END IF;

  -- Optionally resolve a variant by variant_code
  IF p_variant_code IS NOT NULL THEN
    SELECT v.id INTO v_variant_id
    FROM variant v
    JOIN variant_code vc ON vc.variant_id = v.id
    WHERE v.style_id = v_style_id
      AND vc.code = p_variant_code
      AND (p_code_type IS NULL OR vc.code_type = p_code_type)
    LIMIT 1;
    -- If not found, it's fine: we'll save as style-level if v_variant_id stays NULL.
  END IF;

  -- Insert images (idempotent on (style_id, variant_id, url))
  FOREACH l_url IN ARRAY p_urls LOOP
    INSERT INTO product_image(
      style_id, variant_id, region, url, color_code, alt, is_primary, position, source
    )
    VALUES (
      v_style_id, v_variant_id, p_region, l_url, p_color_code, p_alt,
      (l_url = p_primary_url), v_count, 'scrape'
    )
    ON CONFLICT (style_id, variant_id, url) DO NOTHING;

    v_count := v_count + 1;
  END LOOP;

  RETURN v_count;
END;
$$;


--
-- TOC entry 435 (class 1255 OID 17193)
-- Name: apply_rls("jsonb", integer); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION "realtime"."apply_rls"("wal" "jsonb", "max_record_bytes" integer DEFAULT (1024 * 1024)) RETURNS SETOF "realtime"."wal_rls"
    LANGUAGE "plpgsql"
    AS $$
declare
-- Regclass of the table e.g. public.notes
entity_ regclass = (quote_ident(wal ->> 'schema') || '.' || quote_ident(wal ->> 'table'))::regclass;

-- I, U, D, T: insert, update ...
action realtime.action = (
    case wal ->> 'action'
        when 'I' then 'INSERT'
        when 'U' then 'UPDATE'
        when 'D' then 'DELETE'
        else 'ERROR'
    end
);

-- Is row level security enabled for the table
is_rls_enabled bool = relrowsecurity from pg_class where oid = entity_;

subscriptions realtime.subscription[] = array_agg(subs)
    from
        realtime.subscription subs
    where
        subs.entity = entity_;

-- Subscription vars
roles regrole[] = array_agg(distinct us.claims_role::text)
    from
        unnest(subscriptions) us;

working_role regrole;
claimed_role regrole;
claims jsonb;

subscription_id uuid;
subscription_has_access bool;
visible_to_subscription_ids uuid[] = '{}';

-- structured info for wal's columns
columns realtime.wal_column[];
-- previous identity values for update/delete
old_columns realtime.wal_column[];

error_record_exceeds_max_size boolean = octet_length(wal::text) > max_record_bytes;

-- Primary jsonb output for record
output jsonb;

begin
perform set_config('role', null, true);

columns =
    array_agg(
        (
            x->>'name',
            x->>'type',
            x->>'typeoid',
            realtime.cast(
                (x->'value') #>> '{}',
                coalesce(
                    (x->>'typeoid')::regtype, -- null when wal2json version <= 2.4
                    (x->>'type')::regtype
                )
            ),
            (pks ->> 'name') is not null,
            true
        )::realtime.wal_column
    )
    from
        jsonb_array_elements(wal -> 'columns') x
        left join jsonb_array_elements(wal -> 'pk') pks
            on (x ->> 'name') = (pks ->> 'name');

old_columns =
    array_agg(
        (
            x->>'name',
            x->>'type',
            x->>'typeoid',
            realtime.cast(
                (x->'value') #>> '{}',
                coalesce(
                    (x->>'typeoid')::regtype, -- null when wal2json version <= 2.4
                    (x->>'type')::regtype
                )
            ),
            (pks ->> 'name') is not null,
            true
        )::realtime.wal_column
    )
    from
        jsonb_array_elements(wal -> 'identity') x
        left join jsonb_array_elements(wal -> 'pk') pks
            on (x ->> 'name') = (pks ->> 'name');

for working_role in select * from unnest(roles) loop

    -- Update `is_selectable` for columns and old_columns
    columns =
        array_agg(
            (
                c.name,
                c.type_name,
                c.type_oid,
                c.value,
                c.is_pkey,
                pg_catalog.has_column_privilege(working_role, entity_, c.name, 'SELECT')
            )::realtime.wal_column
        )
        from
            unnest(columns) c;

    old_columns =
            array_agg(
                (
                    c.name,
                    c.type_name,
                    c.type_oid,
                    c.value,
                    c.is_pkey,
                    pg_catalog.has_column_privilege(working_role, entity_, c.name, 'SELECT')
                )::realtime.wal_column
            )
            from
                unnest(old_columns) c;

    if action <> 'DELETE' and count(1) = 0 from unnest(columns) c where c.is_pkey then
        return next (
            jsonb_build_object(
                'schema', wal ->> 'schema',
                'table', wal ->> 'table',
                'type', action
            ),
            is_rls_enabled,
            -- subscriptions is already filtered by entity
            (select array_agg(s.subscription_id) from unnest(subscriptions) as s where claims_role = working_role),
            array['Error 400: Bad Request, no primary key']
        )::realtime.wal_rls;

    -- The claims role does not have SELECT permission to the primary key of entity
    elsif action <> 'DELETE' and sum(c.is_selectable::int) <> count(1) from unnest(columns) c where c.is_pkey then
        return next (
            jsonb_build_object(
                'schema', wal ->> 'schema',
                'table', wal ->> 'table',
                'type', action
            ),
            is_rls_enabled,
            (select array_agg(s.subscription_id) from unnest(subscriptions) as s where claims_role = working_role),
            array['Error 401: Unauthorized']
        )::realtime.wal_rls;

    else
        output = jsonb_build_object(
            'schema', wal ->> 'schema',
            'table', wal ->> 'table',
            'type', action,
            'commit_timestamp', to_char(
                ((wal ->> 'timestamp')::timestamptz at time zone 'utc'),
                'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'
            ),
            'columns', (
                select
                    jsonb_agg(
                        jsonb_build_object(
                            'name', pa.attname,
                            'type', pt.typname
                        )
                        order by pa.attnum asc
                    )
                from
                    pg_attribute pa
                    join pg_type pt
                        on pa.atttypid = pt.oid
                where
                    attrelid = entity_
                    and attnum > 0
                    and pg_catalog.has_column_privilege(working_role, entity_, pa.attname, 'SELECT')
            )
        )
        -- Add "record" key for insert and update
        || case
            when action in ('INSERT', 'UPDATE') then
                jsonb_build_object(
                    'record',
                    (
                        select
                            jsonb_object_agg(
                                -- if unchanged toast, get column name and value from old record
                                coalesce((c).name, (oc).name),
                                case
                                    when (c).name is null then (oc).value
                                    else (c).value
                                end
                            )
                        from
                            unnest(columns) c
                            full outer join unnest(old_columns) oc
                                on (c).name = (oc).name
                        where
                            coalesce((c).is_selectable, (oc).is_selectable)
                            and ( not error_record_exceeds_max_size or (octet_length((c).value::text) <= 64))
                    )
                )
            else '{}'::jsonb
        end
        -- Add "old_record" key for update and delete
        || case
            when action = 'UPDATE' then
                jsonb_build_object(
                        'old_record',
                        (
                            select jsonb_object_agg((c).name, (c).value)
                            from unnest(old_columns) c
                            where
                                (c).is_selectable
                                and ( not error_record_exceeds_max_size or (octet_length((c).value::text) <= 64))
                        )
                    )
            when action = 'DELETE' then
                jsonb_build_object(
                    'old_record',
                    (
                        select jsonb_object_agg((c).name, (c).value)
                        from unnest(old_columns) c
                        where
                            (c).is_selectable
                            and ( not error_record_exceeds_max_size or (octet_length((c).value::text) <= 64))
                            and ( not is_rls_enabled or (c).is_pkey ) -- if RLS enabled, we can't secure deletes so filter to pkey
                    )
                )
            else '{}'::jsonb
        end;

        -- Create the prepared statement
        if is_rls_enabled and action <> 'DELETE' then
            if (select 1 from pg_prepared_statements where name = 'walrus_rls_stmt' limit 1) > 0 then
                deallocate walrus_rls_stmt;
            end if;
            execute realtime.build_prepared_statement_sql('walrus_rls_stmt', entity_, columns);
        end if;

        visible_to_subscription_ids = '{}';

        for subscription_id, claims in (
                select
                    subs.subscription_id,
                    subs.claims
                from
                    unnest(subscriptions) subs
                where
                    subs.entity = entity_
                    and subs.claims_role = working_role
                    and (
                        realtime.is_visible_through_filters(columns, subs.filters)
                        or (
                          action = 'DELETE'
                          and realtime.is_visible_through_filters(old_columns, subs.filters)
                        )
                    )
        ) loop

            if not is_rls_enabled or action = 'DELETE' then
                visible_to_subscription_ids = visible_to_subscription_ids || subscription_id;
            else
                -- Check if RLS allows the role to see the record
                perform
                    -- Trim leading and trailing quotes from working_role because set_config
                    -- doesn't recognize the role as valid if they are included
                    set_config('role', trim(both '"' from working_role::text), true),
                    set_config('request.jwt.claims', claims::text, true);

                execute 'execute walrus_rls_stmt' into subscription_has_access;

                if subscription_has_access then
                    visible_to_subscription_ids = visible_to_subscription_ids || subscription_id;
                end if;
            end if;
        end loop;

        perform set_config('role', null, true);

        return next (
            output,
            is_rls_enabled,
            visible_to_subscription_ids,
            case
                when error_record_exceeds_max_size then array['Error 413: Payload Too Large']
                else '{}'
            end
        )::realtime.wal_rls;

    end if;
end loop;

perform set_config('role', null, true);
end;
$$;


--
-- TOC entry 543 (class 1255 OID 17274)
-- Name: broadcast_changes("text", "text", "text", "text", "text", "record", "record", "text"); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION "realtime"."broadcast_changes"("topic_name" "text", "event_name" "text", "operation" "text", "table_name" "text", "table_schema" "text", "new" "record", "old" "record", "level" "text" DEFAULT 'ROW'::"text") RETURNS "void"
    LANGUAGE "plpgsql"
    AS $$
DECLARE
    -- Declare a variable to hold the JSONB representation of the row
    row_data jsonb := '{}'::jsonb;
BEGIN
    IF level = 'STATEMENT' THEN
        RAISE EXCEPTION 'function can only be triggered for each row, not for each statement';
    END IF;
    -- Check the operation type and handle accordingly
    IF operation = 'INSERT' OR operation = 'UPDATE' OR operation = 'DELETE' THEN
        row_data := jsonb_build_object('old_record', OLD, 'record', NEW, 'operation', operation, 'table', table_name, 'schema', table_schema);
        PERFORM realtime.send (row_data, event_name, topic_name);
    ELSE
        RAISE EXCEPTION 'Unexpected operation type: %', operation;
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Failed to process the row: %', SQLERRM;
END;

$$;


--
-- TOC entry 446 (class 1255 OID 17206)
-- Name: build_prepared_statement_sql("text", "regclass", "realtime"."wal_column"[]); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION "realtime"."build_prepared_statement_sql"("prepared_statement_name" "text", "entity" "regclass", "columns" "realtime"."wal_column"[]) RETURNS "text"
    LANGUAGE "sql"
    AS $$
      /*
      Builds a sql string that, if executed, creates a prepared statement to
      tests retrive a row from *entity* by its primary key columns.
      Example
          select realtime.build_prepared_statement_sql('public.notes', '{"id"}'::text[], '{"bigint"}'::text[])
      */
          select
      'prepare ' || prepared_statement_name || ' as
          select
              exists(
                  select
                      1
                  from
                      ' || entity || '
                  where
                      ' || string_agg(quote_ident(pkc.name) || '=' || quote_nullable(pkc.value #>> '{}') , ' and ') || '
              )'
          from
              unnest(columns) pkc
          where
              pkc.is_pkey
          group by
              entity
      $$;


--
-- TOC entry 506 (class 1255 OID 17151)
-- Name: cast("text", "regtype"); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION "realtime"."cast"("val" "text", "type_" "regtype") RETURNS "jsonb"
    LANGUAGE "plpgsql" IMMUTABLE
    AS $$
    declare
      res jsonb;
    begin
      execute format('select to_jsonb(%L::'|| type_::text || ')', val)  into res;
      return res;
    end
    $$;


--
-- TOC entry 440 (class 1255 OID 17146)
-- Name: check_equality_op("realtime"."equality_op", "regtype", "text", "text"); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION "realtime"."check_equality_op"("op" "realtime"."equality_op", "type_" "regtype", "val_1" "text", "val_2" "text") RETURNS boolean
    LANGUAGE "plpgsql" IMMUTABLE
    AS $$
      /*
      Casts *val_1* and *val_2* as type *type_* and check the *op* condition for truthiness
      */
      declare
          op_symbol text = (
              case
                  when op = 'eq' then '='
                  when op = 'neq' then '!='
                  when op = 'lt' then '<'
                  when op = 'lte' then '<='
                  when op = 'gt' then '>'
                  when op = 'gte' then '>='
                  when op = 'in' then '= any'
                  else 'UNKNOWN OP'
              end
          );
          res boolean;
      begin
          execute format(
              'select %L::'|| type_::text || ' ' || op_symbol
              || ' ( %L::'
              || (
                  case
                      when op = 'in' then type_::text || '[]'
                      else type_::text end
              )
              || ')', val_1, val_2) into res;
          return res;
      end;
      $$;


--
-- TOC entry 418 (class 1255 OID 17201)
-- Name: is_visible_through_filters("realtime"."wal_column"[], "realtime"."user_defined_filter"[]); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION "realtime"."is_visible_through_filters"("columns" "realtime"."wal_column"[], "filters" "realtime"."user_defined_filter"[]) RETURNS boolean
    LANGUAGE "sql" IMMUTABLE
    AS $_$
    /*
    Should the record be visible (true) or filtered out (false) after *filters* are applied
    */
        select
            -- Default to allowed when no filters present
            $2 is null -- no filters. this should not happen because subscriptions has a default
            or array_length($2, 1) is null -- array length of an empty array is null
            or bool_and(
                coalesce(
                    realtime.check_equality_op(
                        op:=f.op,
                        type_:=coalesce(
                            col.type_oid::regtype, -- null when wal2json version <= 2.4
                            col.type_name::regtype
                        ),
                        -- cast jsonb to text
                        val_1:=col.value #>> '{}',
                        val_2:=f.value
                    ),
                    false -- if null, filter does not match
                )
            )
        from
            unnest(filters) f
            join unnest(columns) col
                on f.column_name = col.name;
    $_$;


--
-- TOC entry 493 (class 1255 OID 17214)
-- Name: list_changes("name", "name", integer, integer); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION "realtime"."list_changes"("publication" "name", "slot_name" "name", "max_changes" integer, "max_record_bytes" integer) RETURNS SETOF "realtime"."wal_rls"
    LANGUAGE "sql"
    SET "log_min_messages" TO 'fatal'
    AS $$
      with pub as (
        select
          concat_ws(
            ',',
            case when bool_or(pubinsert) then 'insert' else null end,
            case when bool_or(pubupdate) then 'update' else null end,
            case when bool_or(pubdelete) then 'delete' else null end
          ) as w2j_actions,
          coalesce(
            string_agg(
              realtime.quote_wal2json(format('%I.%I', schemaname, tablename)::regclass),
              ','
            ) filter (where ppt.tablename is not null and ppt.tablename not like '% %'),
            ''
          ) w2j_add_tables
        from
          pg_publication pp
          left join pg_publication_tables ppt
            on pp.pubname = ppt.pubname
        where
          pp.pubname = publication
        group by
          pp.pubname
        limit 1
      ),
      w2j as (
        select
          x.*, pub.w2j_add_tables
        from
          pub,
          pg_logical_slot_get_changes(
            slot_name, null, max_changes,
            'include-pk', 'true',
            'include-transaction', 'false',
            'include-timestamp', 'true',
            'include-type-oids', 'true',
            'format-version', '2',
            'actions', pub.w2j_actions,
            'add-tables', pub.w2j_add_tables
          ) x
      )
      select
        xyz.wal,
        xyz.is_rls_enabled,
        xyz.subscription_ids,
        xyz.errors
      from
        w2j,
        realtime.apply_rls(
          wal := w2j.data::jsonb,
          max_record_bytes := max_record_bytes
        ) xyz(wal, is_rls_enabled, subscription_ids, errors)
      where
        w2j.w2j_add_tables <> ''
        and xyz.subscription_ids[1] is not null
    $$;


--
-- TOC entry 538 (class 1255 OID 17145)
-- Name: quote_wal2json("regclass"); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION "realtime"."quote_wal2json"("entity" "regclass") RETURNS "text"
    LANGUAGE "sql" IMMUTABLE STRICT
    AS $$
      select
        (
          select string_agg('' || ch,'')
          from unnest(string_to_array(nsp.nspname::text, null)) with ordinality x(ch, idx)
          where
            not (x.idx = 1 and x.ch = '"')
            and not (
              x.idx = array_length(string_to_array(nsp.nspname::text, null), 1)
              and x.ch = '"'
            )
        )
        || '.'
        || (
          select string_agg('' || ch,'')
          from unnest(string_to_array(pc.relname::text, null)) with ordinality x(ch, idx)
          where
            not (x.idx = 1 and x.ch = '"')
            and not (
              x.idx = array_length(string_to_array(nsp.nspname::text, null), 1)
              and x.ch = '"'
            )
          )
      from
        pg_class pc
        join pg_namespace nsp
          on pc.relnamespace = nsp.oid
      where
        pc.oid = entity
    $$;


--
-- TOC entry 433 (class 1255 OID 17273)
-- Name: send("jsonb", "text", "text", boolean); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION "realtime"."send"("payload" "jsonb", "event" "text", "topic" "text", "private" boolean DEFAULT true) RETURNS "void"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
  BEGIN
    -- Set the topic configuration
    EXECUTE format('SET LOCAL realtime.topic TO %L', topic);

    -- Attempt to insert the message
    INSERT INTO realtime.messages (payload, event, topic, private, extension)
    VALUES (payload, event, topic, private, 'broadcast');
  EXCEPTION
    WHEN OTHERS THEN
      -- Capture and notify the error
      RAISE WARNING 'ErrorSendingBroadcastMessage: %', SQLERRM;
  END;
END;
$$;


--
-- TOC entry 451 (class 1255 OID 17143)
-- Name: subscription_check_filters(); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION "realtime"."subscription_check_filters"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
    /*
    Validates that the user defined filters for a subscription:
    - refer to valid columns that the claimed role may access
    - values are coercable to the correct column type
    */
    declare
        col_names text[] = coalesce(
                array_agg(c.column_name order by c.ordinal_position),
                '{}'::text[]
            )
            from
                information_schema.columns c
            where
                format('%I.%I', c.table_schema, c.table_name)::regclass = new.entity
                and pg_catalog.has_column_privilege(
                    (new.claims ->> 'role'),
                    format('%I.%I', c.table_schema, c.table_name)::regclass,
                    c.column_name,
                    'SELECT'
                );
        filter realtime.user_defined_filter;
        col_type regtype;

        in_val jsonb;
    begin
        for filter in select * from unnest(new.filters) loop
            -- Filtered column is valid
            if not filter.column_name = any(col_names) then
                raise exception 'invalid column for filter %', filter.column_name;
            end if;

            -- Type is sanitized and safe for string interpolation
            col_type = (
                select atttypid::regtype
                from pg_catalog.pg_attribute
                where attrelid = new.entity
                      and attname = filter.column_name
            );
            if col_type is null then
                raise exception 'failed to lookup type for column %', filter.column_name;
            end if;

            -- Set maximum number of entries for in filter
            if filter.op = 'in'::realtime.equality_op then
                in_val = realtime.cast(filter.value, (col_type::text || '[]')::regtype);
                if coalesce(jsonb_array_length(in_val), 0) > 100 then
                    raise exception 'too many values for `in` filter. Maximum 100';
                end if;
            else
                -- raises an exception if value is not coercable to type
                perform realtime.cast(filter.value, col_type);
            end if;

        end loop;

        -- Apply consistent order to filters so the unique constraint on
        -- (subscription_id, entity, filters) can't be tricked by a different filter order
        new.filters = coalesce(
            array_agg(f order by f.column_name, f.op, f.value),
            '{}'
        ) from unnest(new.filters) f;

        return new;
    end;
    $$;


--
-- TOC entry 486 (class 1255 OID 17182)
-- Name: to_regrole("text"); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION "realtime"."to_regrole"("role_name" "text") RETURNS "regrole"
    LANGUAGE "sql" IMMUTABLE
    AS $$ select role_name::regrole $$;


--
-- TOC entry 477 (class 1255 OID 17267)
-- Name: topic(); Type: FUNCTION; Schema: realtime; Owner: -
--

CREATE FUNCTION "realtime"."topic"() RETURNS "text"
    LANGUAGE "sql" STABLE
    AS $$
select nullif(current_setting('realtime.topic', true), '')::text;
$$;


--
-- TOC entry 471 (class 1255 OID 43315)
-- Name: add_prefixes("text", "text"); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."add_prefixes"("_bucket_id" "text", "_name" "text") RETURNS "void"
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
DECLARE
    prefixes text[];
BEGIN
    prefixes := "storage"."get_prefixes"("_name");

    IF array_length(prefixes, 1) > 0 THEN
        INSERT INTO storage.prefixes (name, bucket_id)
        SELECT UNNEST(prefixes) as name, "_bucket_id" ON CONFLICT DO NOTHING;
    END IF;
END;
$$;


--
-- TOC entry 463 (class 1255 OID 17058)
-- Name: can_insert_object("text", "text", "uuid", "jsonb"); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."can_insert_object"("bucketid" "text", "name" "text", "owner" "uuid", "metadata" "jsonb") RETURNS "void"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
  INSERT INTO "storage"."objects" ("bucket_id", "name", "owner", "metadata") VALUES (bucketid, name, owner, metadata);
  -- hack to rollback the successful insert
  RAISE sqlstate 'PT200' using
  message = 'ROLLBACK',
  detail = 'rollback successful insert';
END
$$;


--
-- TOC entry 434 (class 1255 OID 43355)
-- Name: delete_leaf_prefixes("text"[], "text"[]); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."delete_leaf_prefixes"("bucket_ids" "text"[], "names" "text"[]) RETURNS "void"
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
DECLARE
    v_rows_deleted integer;
BEGIN
    LOOP
        WITH candidates AS (
            SELECT DISTINCT
                t.bucket_id,
                unnest(storage.get_prefixes(t.name)) AS name
            FROM unnest(bucket_ids, names) AS t(bucket_id, name)
        ),
        uniq AS (
             SELECT
                 bucket_id,
                 name,
                 storage.get_level(name) AS level
             FROM candidates
             WHERE name <> ''
             GROUP BY bucket_id, name
        ),
        leaf AS (
             SELECT
                 p.bucket_id,
                 p.name,
                 p.level
             FROM storage.prefixes AS p
                  JOIN uniq AS u
                       ON u.bucket_id = p.bucket_id
                           AND u.name = p.name
                           AND u.level = p.level
             WHERE NOT EXISTS (
                 SELECT 1
                 FROM storage.objects AS o
                 WHERE o.bucket_id = p.bucket_id
                   AND o.level = p.level + 1
                   AND o.name COLLATE "C" LIKE p.name || '/%'
             )
             AND NOT EXISTS (
                 SELECT 1
                 FROM storage.prefixes AS c
                 WHERE c.bucket_id = p.bucket_id
                   AND c.level = p.level + 1
                   AND c.name COLLATE "C" LIKE p.name || '/%'
             )
        )
        DELETE
        FROM storage.prefixes AS p
            USING leaf AS l
        WHERE p.bucket_id = l.bucket_id
          AND p.name = l.name
          AND p.level = l.level;

        GET DIAGNOSTICS v_rows_deleted = ROW_COUNT;
        EXIT WHEN v_rows_deleted = 0;
    END LOOP;
END;
$$;


--
-- TOC entry 499 (class 1255 OID 43316)
-- Name: delete_prefix("text", "text"); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."delete_prefix"("_bucket_id" "text", "_name" "text") RETURNS boolean
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
BEGIN
    -- Check if we can delete the prefix
    IF EXISTS(
        SELECT FROM "storage"."prefixes"
        WHERE "prefixes"."bucket_id" = "_bucket_id"
          AND level = "storage"."get_level"("_name") + 1
          AND "prefixes"."name" COLLATE "C" LIKE "_name" || '/%'
        LIMIT 1
    )
    OR EXISTS(
        SELECT FROM "storage"."objects"
        WHERE "objects"."bucket_id" = "_bucket_id"
          AND "storage"."get_level"("objects"."name") = "storage"."get_level"("_name") + 1
          AND "objects"."name" COLLATE "C" LIKE "_name" || '/%'
        LIMIT 1
    ) THEN
    -- There are sub-objects, skip deletion
    RETURN false;
    ELSE
        DELETE FROM "storage"."prefixes"
        WHERE "prefixes"."bucket_id" = "_bucket_id"
          AND level = "storage"."get_level"("_name")
          AND "prefixes"."name" = "_name";
        RETURN true;
    END IF;
END;
$$;


--
-- TOC entry 480 (class 1255 OID 43319)
-- Name: delete_prefix_hierarchy_trigger(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."delete_prefix_hierarchy_trigger"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
DECLARE
    prefix text;
BEGIN
    prefix := "storage"."get_prefix"(OLD."name");

    IF coalesce(prefix, '') != '' THEN
        PERFORM "storage"."delete_prefix"(OLD."bucket_id", prefix);
    END IF;

    RETURN OLD;
END;
$$;


--
-- TOC entry 533 (class 1255 OID 43334)
-- Name: enforce_bucket_name_length(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."enforce_bucket_name_length"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
begin
    if length(new.name) > 100 then
        raise exception 'bucket name "%" is too long (% characters). Max is 100.', new.name, length(new.name);
    end if;
    return new;
end;
$$;


--
-- TOC entry 488 (class 1255 OID 17032)
-- Name: extension("text"); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."extension"("name" "text") RETURNS "text"
    LANGUAGE "plpgsql" IMMUTABLE
    AS $$
DECLARE
    _parts text[];
    _filename text;
BEGIN
    SELECT string_to_array(name, '/') INTO _parts;
    SELECT _parts[array_length(_parts,1)] INTO _filename;
    RETURN reverse(split_part(reverse(_filename), '.', 1));
END
$$;


--
-- TOC entry 547 (class 1255 OID 17031)
-- Name: filename("text"); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."filename"("name" "text") RETURNS "text"
    LANGUAGE "plpgsql"
    AS $$
DECLARE
_parts text[];
BEGIN
	select string_to_array(name, '/') into _parts;
	return _parts[array_length(_parts,1)];
END
$$;


--
-- TOC entry 491 (class 1255 OID 17030)
-- Name: foldername("text"); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."foldername"("name" "text") RETURNS "text"[]
    LANGUAGE "plpgsql" IMMUTABLE
    AS $$
DECLARE
    _parts text[];
BEGIN
    -- Split on "/" to get path segments
    SELECT string_to_array(name, '/') INTO _parts;
    -- Return everything except the last segment
    RETURN _parts[1 : array_length(_parts,1) - 1];
END
$$;


--
-- TOC entry 545 (class 1255 OID 43297)
-- Name: get_level("text"); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."get_level"("name" "text") RETURNS integer
    LANGUAGE "sql" IMMUTABLE STRICT
    AS $$
SELECT array_length(string_to_array("name", '/'), 1);
$$;


--
-- TOC entry 546 (class 1255 OID 43313)
-- Name: get_prefix("text"); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."get_prefix"("name" "text") RETURNS "text"
    LANGUAGE "sql" IMMUTABLE STRICT
    AS $_$
SELECT
    CASE WHEN strpos("name", '/') > 0 THEN
             regexp_replace("name", '[\/]{1}[^\/]+\/?$', '')
         ELSE
             ''
        END;
$_$;


--
-- TOC entry 523 (class 1255 OID 43314)
-- Name: get_prefixes("text"); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."get_prefixes"("name" "text") RETURNS "text"[]
    LANGUAGE "plpgsql" IMMUTABLE STRICT
    AS $$
DECLARE
    parts text[];
    prefixes text[];
    prefix text;
BEGIN
    -- Split the name into parts by '/'
    parts := string_to_array("name", '/');
    prefixes := '{}';

    -- Construct the prefixes, stopping one level below the last part
    FOR i IN 1..array_length(parts, 1) - 1 LOOP
            prefix := array_to_string(parts[1:i], '/');
            prefixes := array_append(prefixes, prefix);
    END LOOP;

    RETURN prefixes;
END;
$$;


--
-- TOC entry 479 (class 1255 OID 43332)
-- Name: get_size_by_bucket(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."get_size_by_bucket"() RETURNS TABLE("size" bigint, "bucket_id" "text")
    LANGUAGE "plpgsql" STABLE
    AS $$
BEGIN
    return query
        select sum((metadata->>'size')::bigint) as size, obj.bucket_id
        from "storage".objects as obj
        group by obj.bucket_id;
END
$$;


--
-- TOC entry 465 (class 1255 OID 17097)
-- Name: list_multipart_uploads_with_delimiter("text", "text", "text", integer, "text", "text"); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."list_multipart_uploads_with_delimiter"("bucket_id" "text", "prefix_param" "text", "delimiter_param" "text", "max_keys" integer DEFAULT 100, "next_key_token" "text" DEFAULT ''::"text", "next_upload_token" "text" DEFAULT ''::"text") RETURNS TABLE("key" "text", "id" "text", "created_at" timestamp with time zone)
    LANGUAGE "plpgsql"
    AS $_$
BEGIN
    RETURN QUERY EXECUTE
        'SELECT DISTINCT ON(key COLLATE "C") * from (
            SELECT
                CASE
                    WHEN position($2 IN substring(key from length($1) + 1)) > 0 THEN
                        substring(key from 1 for length($1) + position($2 IN substring(key from length($1) + 1)))
                    ELSE
                        key
                END AS key, id, created_at
            FROM
                storage.s3_multipart_uploads
            WHERE
                bucket_id = $5 AND
                key ILIKE $1 || ''%'' AND
                CASE
                    WHEN $4 != '''' AND $6 = '''' THEN
                        CASE
                            WHEN position($2 IN substring(key from length($1) + 1)) > 0 THEN
                                substring(key from 1 for length($1) + position($2 IN substring(key from length($1) + 1))) COLLATE "C" > $4
                            ELSE
                                key COLLATE "C" > $4
                            END
                    ELSE
                        true
                END AND
                CASE
                    WHEN $6 != '''' THEN
                        id COLLATE "C" > $6
                    ELSE
                        true
                    END
            ORDER BY
                key COLLATE "C" ASC, created_at ASC) as e order by key COLLATE "C" LIMIT $3'
        USING prefix_param, delimiter_param, max_keys, next_key_token, bucket_id, next_upload_token;
END;
$_$;


--
-- TOC entry 447 (class 1255 OID 17060)
-- Name: list_objects_with_delimiter("text", "text", "text", integer, "text", "text"); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."list_objects_with_delimiter"("bucket_id" "text", "prefix_param" "text", "delimiter_param" "text", "max_keys" integer DEFAULT 100, "start_after" "text" DEFAULT ''::"text", "next_token" "text" DEFAULT ''::"text") RETURNS TABLE("name" "text", "id" "uuid", "metadata" "jsonb", "updated_at" timestamp with time zone)
    LANGUAGE "plpgsql"
    AS $_$
BEGIN
    RETURN QUERY EXECUTE
        'SELECT DISTINCT ON(name COLLATE "C") * from (
            SELECT
                CASE
                    WHEN position($2 IN substring(name from length($1) + 1)) > 0 THEN
                        substring(name from 1 for length($1) + position($2 IN substring(name from length($1) + 1)))
                    ELSE
                        name
                END AS name, id, metadata, updated_at
            FROM
                storage.objects
            WHERE
                bucket_id = $5 AND
                name ILIKE $1 || ''%'' AND
                CASE
                    WHEN $6 != '''' THEN
                    name COLLATE "C" > $6
                ELSE true END
                AND CASE
                    WHEN $4 != '''' THEN
                        CASE
                            WHEN position($2 IN substring(name from length($1) + 1)) > 0 THEN
                                substring(name from 1 for length($1) + position($2 IN substring(name from length($1) + 1))) COLLATE "C" > $4
                            ELSE
                                name COLLATE "C" > $4
                            END
                    ELSE
                        true
                END
            ORDER BY
                name COLLATE "C" ASC) as e order by name COLLATE "C" LIMIT $3'
        USING prefix_param, delimiter_param, max_keys, next_token, bucket_id, start_after;
END;
$_$;


--
-- TOC entry 450 (class 1255 OID 43354)
-- Name: lock_top_prefixes("text"[], "text"[]); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."lock_top_prefixes"("bucket_ids" "text"[], "names" "text"[]) RETURNS "void"
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
DECLARE
    v_bucket text;
    v_top text;
BEGIN
    FOR v_bucket, v_top IN
        SELECT DISTINCT t.bucket_id,
            split_part(t.name, '/', 1) AS top
        FROM unnest(bucket_ids, names) AS t(bucket_id, name)
        WHERE t.name <> ''
        ORDER BY 1, 2
        LOOP
            PERFORM pg_advisory_xact_lock(hashtextextended(v_bucket || '/' || v_top, 0));
        END LOOP;
END;
$$;


--
-- TOC entry 466 (class 1255 OID 43356)
-- Name: objects_delete_cleanup(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."objects_delete_cleanup"() RETURNS "trigger"
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
DECLARE
    v_bucket_ids text[];
    v_names      text[];
BEGIN
    IF current_setting('storage.gc.prefixes', true) = '1' THEN
        RETURN NULL;
    END IF;

    PERFORM set_config('storage.gc.prefixes', '1', true);

    SELECT COALESCE(array_agg(d.bucket_id), '{}'),
           COALESCE(array_agg(d.name), '{}')
    INTO v_bucket_ids, v_names
    FROM deleted AS d
    WHERE d.name <> '';

    PERFORM storage.lock_top_prefixes(v_bucket_ids, v_names);
    PERFORM storage.delete_leaf_prefixes(v_bucket_ids, v_names);

    RETURN NULL;
END;
$$;


--
-- TOC entry 478 (class 1255 OID 43318)
-- Name: objects_insert_prefix_trigger(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."objects_insert_prefix_trigger"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    PERFORM "storage"."add_prefixes"(NEW."bucket_id", NEW."name");
    NEW.level := "storage"."get_level"(NEW."name");

    RETURN NEW;
END;
$$;


--
-- TOC entry 424 (class 1255 OID 43357)
-- Name: objects_update_cleanup(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."objects_update_cleanup"() RETURNS "trigger"
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
DECLARE
    -- NEW - OLD (destinations to create prefixes for)
    v_add_bucket_ids text[];
    v_add_names      text[];

    -- OLD - NEW (sources to prune)
    v_src_bucket_ids text[];
    v_src_names      text[];
BEGIN
    IF TG_OP <> 'UPDATE' THEN
        RETURN NULL;
    END IF;

    -- 1) Compute NEW−OLD (added paths) and OLD−NEW (moved-away paths)
    WITH added AS (
        SELECT n.bucket_id, n.name
        FROM new_rows n
        WHERE n.name <> '' AND position('/' in n.name) > 0
        EXCEPT
        SELECT o.bucket_id, o.name FROM old_rows o WHERE o.name <> ''
    ),
    moved AS (
         SELECT o.bucket_id, o.name
         FROM old_rows o
         WHERE o.name <> ''
         EXCEPT
         SELECT n.bucket_id, n.name FROM new_rows n WHERE n.name <> ''
    )
    SELECT
        -- arrays for ADDED (dest) in stable order
        COALESCE( (SELECT array_agg(a.bucket_id ORDER BY a.bucket_id, a.name) FROM added a), '{}' ),
        COALESCE( (SELECT array_agg(a.name      ORDER BY a.bucket_id, a.name) FROM added a), '{}' ),
        -- arrays for MOVED (src) in stable order
        COALESCE( (SELECT array_agg(m.bucket_id ORDER BY m.bucket_id, m.name) FROM moved m), '{}' ),
        COALESCE( (SELECT array_agg(m.name      ORDER BY m.bucket_id, m.name) FROM moved m), '{}' )
    INTO v_add_bucket_ids, v_add_names, v_src_bucket_ids, v_src_names;

    -- Nothing to do?
    IF (array_length(v_add_bucket_ids, 1) IS NULL) AND (array_length(v_src_bucket_ids, 1) IS NULL) THEN
        RETURN NULL;
    END IF;

    -- 2) Take per-(bucket, top) locks: ALL prefixes in consistent global order to prevent deadlocks
    DECLARE
        v_all_bucket_ids text[];
        v_all_names text[];
    BEGIN
        -- Combine source and destination arrays for consistent lock ordering
        v_all_bucket_ids := COALESCE(v_src_bucket_ids, '{}') || COALESCE(v_add_bucket_ids, '{}');
        v_all_names := COALESCE(v_src_names, '{}') || COALESCE(v_add_names, '{}');

        -- Single lock call ensures consistent global ordering across all transactions
        IF array_length(v_all_bucket_ids, 1) IS NOT NULL THEN
            PERFORM storage.lock_top_prefixes(v_all_bucket_ids, v_all_names);
        END IF;
    END;

    -- 3) Create destination prefixes (NEW−OLD) BEFORE pruning sources
    IF array_length(v_add_bucket_ids, 1) IS NOT NULL THEN
        WITH candidates AS (
            SELECT DISTINCT t.bucket_id, unnest(storage.get_prefixes(t.name)) AS name
            FROM unnest(v_add_bucket_ids, v_add_names) AS t(bucket_id, name)
            WHERE name <> ''
        )
        INSERT INTO storage.prefixes (bucket_id, name)
        SELECT c.bucket_id, c.name
        FROM candidates c
        ON CONFLICT DO NOTHING;
    END IF;

    -- 4) Prune source prefixes bottom-up for OLD−NEW
    IF array_length(v_src_bucket_ids, 1) IS NOT NULL THEN
        -- re-entrancy guard so DELETE on prefixes won't recurse
        IF current_setting('storage.gc.prefixes', true) <> '1' THEN
            PERFORM set_config('storage.gc.prefixes', '1', true);
        END IF;

        PERFORM storage.delete_leaf_prefixes(v_src_bucket_ids, v_src_names);
    END IF;

    RETURN NULL;
END;
$$;


--
-- TOC entry 484 (class 1255 OID 43362)
-- Name: objects_update_level_trigger(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."objects_update_level_trigger"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    -- Ensure this is an update operation and the name has changed
    IF TG_OP = 'UPDATE' AND (NEW."name" <> OLD."name" OR NEW."bucket_id" <> OLD."bucket_id") THEN
        -- Set the new level
        NEW."level" := "storage"."get_level"(NEW."name");
    END IF;
    RETURN NEW;
END;
$$;


--
-- TOC entry 437 (class 1255 OID 43333)
-- Name: objects_update_prefix_trigger(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."objects_update_prefix_trigger"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
DECLARE
    old_prefixes TEXT[];
BEGIN
    -- Ensure this is an update operation and the name has changed
    IF TG_OP = 'UPDATE' AND (NEW."name" <> OLD."name" OR NEW."bucket_id" <> OLD."bucket_id") THEN
        -- Retrieve old prefixes
        old_prefixes := "storage"."get_prefixes"(OLD."name");

        -- Remove old prefixes that are only used by this object
        WITH all_prefixes as (
            SELECT unnest(old_prefixes) as prefix
        ),
        can_delete_prefixes as (
             SELECT prefix
             FROM all_prefixes
             WHERE NOT EXISTS (
                 SELECT 1 FROM "storage"."objects"
                 WHERE "bucket_id" = OLD."bucket_id"
                   AND "name" <> OLD."name"
                   AND "name" LIKE (prefix || '%')
             )
         )
        DELETE FROM "storage"."prefixes" WHERE name IN (SELECT prefix FROM can_delete_prefixes);

        -- Add new prefixes
        PERFORM "storage"."add_prefixes"(NEW."bucket_id", NEW."name");
    END IF;
    -- Set the new level
    NEW."level" := "storage"."get_level"(NEW."name");

    RETURN NEW;
END;
$$;


--
-- TOC entry 475 (class 1255 OID 17113)
-- Name: operation(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."operation"() RETURNS "text"
    LANGUAGE "plpgsql" STABLE
    AS $$
BEGIN
    RETURN current_setting('storage.operation', true);
END;
$$;


--
-- TOC entry 420 (class 1255 OID 43358)
-- Name: prefixes_delete_cleanup(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."prefixes_delete_cleanup"() RETURNS "trigger"
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
DECLARE
    v_bucket_ids text[];
    v_names      text[];
BEGIN
    IF current_setting('storage.gc.prefixes', true) = '1' THEN
        RETURN NULL;
    END IF;

    PERFORM set_config('storage.gc.prefixes', '1', true);

    SELECT COALESCE(array_agg(d.bucket_id), '{}'),
           COALESCE(array_agg(d.name), '{}')
    INTO v_bucket_ids, v_names
    FROM deleted AS d
    WHERE d.name <> '';

    PERFORM storage.lock_top_prefixes(v_bucket_ids, v_names);
    PERFORM storage.delete_leaf_prefixes(v_bucket_ids, v_names);

    RETURN NULL;
END;
$$;


--
-- TOC entry 439 (class 1255 OID 43317)
-- Name: prefixes_insert_trigger(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."prefixes_insert_trigger"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    PERFORM "storage"."add_prefixes"(NEW."bucket_id", NEW."name");
    RETURN NEW;
END;
$$;


--
-- TOC entry 496 (class 1255 OID 17047)
-- Name: search("text", "text", integer, integer, integer, "text", "text", "text"); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."search"("prefix" "text", "bucketname" "text", "limits" integer DEFAULT 100, "levels" integer DEFAULT 1, "offsets" integer DEFAULT 0, "search" "text" DEFAULT ''::"text", "sortcolumn" "text" DEFAULT 'name'::"text", "sortorder" "text" DEFAULT 'asc'::"text") RETURNS TABLE("name" "text", "id" "uuid", "updated_at" timestamp with time zone, "created_at" timestamp with time zone, "last_accessed_at" timestamp with time zone, "metadata" "jsonb")
    LANGUAGE "plpgsql"
    AS $$
declare
    can_bypass_rls BOOLEAN;
begin
    SELECT rolbypassrls
    INTO can_bypass_rls
    FROM pg_roles
    WHERE rolname = coalesce(nullif(current_setting('role', true), 'none'), current_user);

    IF can_bypass_rls THEN
        RETURN QUERY SELECT * FROM storage.search_v1_optimised(prefix, bucketname, limits, levels, offsets, search, sortcolumn, sortorder);
    ELSE
        RETURN QUERY SELECT * FROM storage.search_legacy_v1(prefix, bucketname, limits, levels, offsets, search, sortcolumn, sortorder);
    END IF;
end;
$$;


--
-- TOC entry 449 (class 1255 OID 43330)
-- Name: search_legacy_v1("text", "text", integer, integer, integer, "text", "text", "text"); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."search_legacy_v1"("prefix" "text", "bucketname" "text", "limits" integer DEFAULT 100, "levels" integer DEFAULT 1, "offsets" integer DEFAULT 0, "search" "text" DEFAULT ''::"text", "sortcolumn" "text" DEFAULT 'name'::"text", "sortorder" "text" DEFAULT 'asc'::"text") RETURNS TABLE("name" "text", "id" "uuid", "updated_at" timestamp with time zone, "created_at" timestamp with time zone, "last_accessed_at" timestamp with time zone, "metadata" "jsonb")
    LANGUAGE "plpgsql" STABLE
    AS $_$
declare
    v_order_by text;
    v_sort_order text;
begin
    case
        when sortcolumn = 'name' then
            v_order_by = 'name';
        when sortcolumn = 'updated_at' then
            v_order_by = 'updated_at';
        when sortcolumn = 'created_at' then
            v_order_by = 'created_at';
        when sortcolumn = 'last_accessed_at' then
            v_order_by = 'last_accessed_at';
        else
            v_order_by = 'name';
        end case;

    case
        when sortorder = 'asc' then
            v_sort_order = 'asc';
        when sortorder = 'desc' then
            v_sort_order = 'desc';
        else
            v_sort_order = 'asc';
        end case;

    v_order_by = v_order_by || ' ' || v_sort_order;

    return query execute
        'with folders as (
           select path_tokens[$1] as folder
           from storage.objects
             where objects.name ilike $2 || $3 || ''%''
               and bucket_id = $4
               and array_length(objects.path_tokens, 1) <> $1
           group by folder
           order by folder ' || v_sort_order || '
     )
     (select folder as "name",
            null as id,
            null as updated_at,
            null as created_at,
            null as last_accessed_at,
            null as metadata from folders)
     union all
     (select path_tokens[$1] as "name",
            id,
            updated_at,
            created_at,
            last_accessed_at,
            metadata
     from storage.objects
     where objects.name ilike $2 || $3 || ''%''
       and bucket_id = $4
       and array_length(objects.path_tokens, 1) = $1
     order by ' || v_order_by || ')
     limit $5
     offset $6' using levels, prefix, search, bucketname, limits, offsets;
end;
$_$;


--
-- TOC entry 455 (class 1255 OID 43329)
-- Name: search_v1_optimised("text", "text", integer, integer, integer, "text", "text", "text"); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."search_v1_optimised"("prefix" "text", "bucketname" "text", "limits" integer DEFAULT 100, "levels" integer DEFAULT 1, "offsets" integer DEFAULT 0, "search" "text" DEFAULT ''::"text", "sortcolumn" "text" DEFAULT 'name'::"text", "sortorder" "text" DEFAULT 'asc'::"text") RETURNS TABLE("name" "text", "id" "uuid", "updated_at" timestamp with time zone, "created_at" timestamp with time zone, "last_accessed_at" timestamp with time zone, "metadata" "jsonb")
    LANGUAGE "plpgsql" STABLE
    AS $_$
declare
    v_order_by text;
    v_sort_order text;
begin
    case
        when sortcolumn = 'name' then
            v_order_by = 'name';
        when sortcolumn = 'updated_at' then
            v_order_by = 'updated_at';
        when sortcolumn = 'created_at' then
            v_order_by = 'created_at';
        when sortcolumn = 'last_accessed_at' then
            v_order_by = 'last_accessed_at';
        else
            v_order_by = 'name';
        end case;

    case
        when sortorder = 'asc' then
            v_sort_order = 'asc';
        when sortorder = 'desc' then
            v_sort_order = 'desc';
        else
            v_sort_order = 'asc';
        end case;

    v_order_by = v_order_by || ' ' || v_sort_order;

    return query execute
        'with folders as (
           select (string_to_array(name, ''/''))[level] as name
           from storage.prefixes
             where lower(prefixes.name) like lower($2 || $3) || ''%''
               and bucket_id = $4
               and level = $1
           order by name ' || v_sort_order || '
     )
     (select name,
            null as id,
            null as updated_at,
            null as created_at,
            null as last_accessed_at,
            null as metadata from folders)
     union all
     (select path_tokens[level] as "name",
            id,
            updated_at,
            created_at,
            last_accessed_at,
            metadata
     from storage.objects
     where lower(objects.name) like lower($2 || $3) || ''%''
       and bucket_id = $4
       and level = $1
     order by ' || v_order_by || ')
     limit $5
     offset $6' using levels, prefix, search, bucketname, limits, offsets;
end;
$_$;


--
-- TOC entry 529 (class 1255 OID 43353)
-- Name: search_v2("text", "text", integer, integer, "text", "text", "text", "text"); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."search_v2"("prefix" "text", "bucket_name" "text", "limits" integer DEFAULT 100, "levels" integer DEFAULT 1, "start_after" "text" DEFAULT ''::"text", "sort_order" "text" DEFAULT 'asc'::"text", "sort_column" "text" DEFAULT 'name'::"text", "sort_column_after" "text" DEFAULT ''::"text") RETURNS TABLE("key" "text", "name" "text", "id" "uuid", "updated_at" timestamp with time zone, "created_at" timestamp with time zone, "last_accessed_at" timestamp with time zone, "metadata" "jsonb")
    LANGUAGE "plpgsql" STABLE
    AS $_$
DECLARE
    sort_col text;
    sort_ord text;
    cursor_op text;
    cursor_expr text;
    sort_expr text;
BEGIN
    -- Validate sort_order
    sort_ord := lower(sort_order);
    IF sort_ord NOT IN ('asc', 'desc') THEN
        sort_ord := 'asc';
    END IF;

    -- Determine cursor comparison operator
    IF sort_ord = 'asc' THEN
        cursor_op := '>';
    ELSE
        cursor_op := '<';
    END IF;
    
    sort_col := lower(sort_column);
    -- Validate sort column  
    IF sort_col IN ('updated_at', 'created_at') THEN
        cursor_expr := format(
            '($5 = '''' OR ROW(date_trunc(''milliseconds'', %I), name COLLATE "C") %s ROW(COALESCE(NULLIF($6, '''')::timestamptz, ''epoch''::timestamptz), $5))',
            sort_col, cursor_op
        );
        sort_expr := format(
            'COALESCE(date_trunc(''milliseconds'', %I), ''epoch''::timestamptz) %s, name COLLATE "C" %s',
            sort_col, sort_ord, sort_ord
        );
    ELSE
        cursor_expr := format('($5 = '''' OR name COLLATE "C" %s $5)', cursor_op);
        sort_expr := format('name COLLATE "C" %s', sort_ord);
    END IF;

    RETURN QUERY EXECUTE format(
        $sql$
        SELECT * FROM (
            (
                SELECT
                    split_part(name, '/', $4) AS key,
                    name,
                    NULL::uuid AS id,
                    updated_at,
                    created_at,
                    NULL::timestamptz AS last_accessed_at,
                    NULL::jsonb AS metadata
                FROM storage.prefixes
                WHERE name COLLATE "C" LIKE $1 || '%%'
                    AND bucket_id = $2
                    AND level = $4
                    AND %s
                ORDER BY %s
                LIMIT $3
            )
            UNION ALL
            (
                SELECT
                    split_part(name, '/', $4) AS key,
                    name,
                    id,
                    updated_at,
                    created_at,
                    last_accessed_at,
                    metadata
                FROM storage.objects
                WHERE name COLLATE "C" LIKE $1 || '%%'
                    AND bucket_id = $2
                    AND level = $4
                    AND %s
                ORDER BY %s
                LIMIT $3
            )
        ) obj
        ORDER BY %s
        LIMIT $3
        $sql$,
        cursor_expr,    -- prefixes WHERE
        sort_expr,      -- prefixes ORDER BY
        cursor_expr,    -- objects WHERE
        sort_expr,      -- objects ORDER BY
        sort_expr       -- final ORDER BY
    )
    USING prefix, bucket_name, limits, levels, start_after, sort_column_after;
END;
$_$;


--
-- TOC entry 520 (class 1255 OID 17048)
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: storage; Owner: -
--

CREATE FUNCTION "storage"."update_updated_at_column"() RETURNS "trigger"
    LANGUAGE "plpgsql"
    AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW; 
END;
$$;


--
-- TOC entry 472 (class 1255 OID 23433)
-- Name: http_request(); Type: FUNCTION; Schema: supabase_functions; Owner: -
--

CREATE FUNCTION "supabase_functions"."http_request"() RETURNS "trigger"
    LANGUAGE "plpgsql" SECURITY DEFINER
    SET "search_path" TO 'supabase_functions'
    AS $$
    DECLARE
      request_id bigint;
      payload jsonb;
      url text := TG_ARGV[0]::text;
      method text := TG_ARGV[1]::text;
      headers jsonb DEFAULT '{}'::jsonb;
      params jsonb DEFAULT '{}'::jsonb;
      timeout_ms integer DEFAULT 1000;
    BEGIN
      IF url IS NULL OR url = 'null' THEN
        RAISE EXCEPTION 'url argument is missing';
      END IF;

      IF method IS NULL OR method = 'null' THEN
        RAISE EXCEPTION 'method argument is missing';
      END IF;

      IF TG_ARGV[2] IS NULL OR TG_ARGV[2] = 'null' THEN
        headers = '{"Content-Type": "application/json"}'::jsonb;
      ELSE
        headers = TG_ARGV[2]::jsonb;
      END IF;

      IF TG_ARGV[3] IS NULL OR TG_ARGV[3] = 'null' THEN
        params = '{}'::jsonb;
      ELSE
        params = TG_ARGV[3]::jsonb;
      END IF;

      IF TG_ARGV[4] IS NULL OR TG_ARGV[4] = 'null' THEN
        timeout_ms = 1000;
      ELSE
        timeout_ms = TG_ARGV[4]::integer;
      END IF;

      CASE
        WHEN method = 'GET' THEN
          SELECT http_get INTO request_id FROM net.http_get(
            url,
            params,
            headers,
            timeout_ms
          );
        WHEN method = 'POST' THEN
          payload = jsonb_build_object(
            'old_record', OLD,
            'record', NEW,
            'type', TG_OP,
            'table', TG_TABLE_NAME,
            'schema', TG_TABLE_SCHEMA
          );

          SELECT http_post INTO request_id FROM net.http_post(
            url,
            payload,
            params,
            headers,
            timeout_ms
          );
        ELSE
          RAISE EXCEPTION 'method argument % is invalid', method;
      END CASE;

      INSERT INTO supabase_functions.hooks
        (hook_table_id, hook_name, request_id)
      VALUES
        (TG_RELID, TG_NAME, request_id);

      RETURN NEW;
    END
  $$;


SET default_tablespace = '';

SET default_table_access_method = "heap";

--
-- TOC entry 327 (class 1259 OID 16525)
-- Name: audit_log_entries; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE "auth"."audit_log_entries" (
    "instance_id" "uuid",
    "id" "uuid" NOT NULL,
    "payload" json,
    "created_at" timestamp with time zone,
    "ip_address" character varying(64) DEFAULT ''::character varying NOT NULL
);


--
-- TOC entry 4423 (class 0 OID 0)
-- Dependencies: 327
-- Name: TABLE "audit_log_entries"; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE "auth"."audit_log_entries" IS 'Auth: Audit trail for user actions.';


--
-- TOC entry 344 (class 1259 OID 16927)
-- Name: flow_state; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE "auth"."flow_state" (
    "id" "uuid" NOT NULL,
    "user_id" "uuid",
    "auth_code" "text" NOT NULL,
    "code_challenge_method" "auth"."code_challenge_method" NOT NULL,
    "code_challenge" "text" NOT NULL,
    "provider_type" "text" NOT NULL,
    "provider_access_token" "text",
    "provider_refresh_token" "text",
    "created_at" timestamp with time zone,
    "updated_at" timestamp with time zone,
    "authentication_method" "text" NOT NULL,
    "auth_code_issued_at" timestamp with time zone
);


--
-- TOC entry 4424 (class 0 OID 0)
-- Dependencies: 344
-- Name: TABLE "flow_state"; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE "auth"."flow_state" IS 'stores metadata for pkce logins';


--
-- TOC entry 335 (class 1259 OID 16725)
-- Name: identities; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE "auth"."identities" (
    "provider_id" "text" NOT NULL,
    "user_id" "uuid" NOT NULL,
    "identity_data" "jsonb" NOT NULL,
    "provider" "text" NOT NULL,
    "last_sign_in_at" timestamp with time zone,
    "created_at" timestamp with time zone,
    "updated_at" timestamp with time zone,
    "email" "text" GENERATED ALWAYS AS ("lower"(("identity_data" ->> 'email'::"text"))) STORED,
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL
);


--
-- TOC entry 4425 (class 0 OID 0)
-- Dependencies: 335
-- Name: TABLE "identities"; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE "auth"."identities" IS 'Auth: Stores identities associated to a user.';


--
-- TOC entry 4426 (class 0 OID 0)
-- Dependencies: 335
-- Name: COLUMN "identities"."email"; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON COLUMN "auth"."identities"."email" IS 'Auth: Email is a generated column that references the optional email property in the identity_data';


--
-- TOC entry 326 (class 1259 OID 16518)
-- Name: instances; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE "auth"."instances" (
    "id" "uuid" NOT NULL,
    "uuid" "uuid",
    "raw_base_config" "text",
    "created_at" timestamp with time zone,
    "updated_at" timestamp with time zone
);


--
-- TOC entry 4427 (class 0 OID 0)
-- Dependencies: 326
-- Name: TABLE "instances"; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE "auth"."instances" IS 'Auth: Manages users across multiple sites.';


--
-- TOC entry 339 (class 1259 OID 16814)
-- Name: mfa_amr_claims; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE "auth"."mfa_amr_claims" (
    "session_id" "uuid" NOT NULL,
    "created_at" timestamp with time zone NOT NULL,
    "updated_at" timestamp with time zone NOT NULL,
    "authentication_method" "text" NOT NULL,
    "id" "uuid" NOT NULL
);


--
-- TOC entry 4428 (class 0 OID 0)
-- Dependencies: 339
-- Name: TABLE "mfa_amr_claims"; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE "auth"."mfa_amr_claims" IS 'auth: stores authenticator method reference claims for multi factor authentication';


--
-- TOC entry 338 (class 1259 OID 16802)
-- Name: mfa_challenges; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE "auth"."mfa_challenges" (
    "id" "uuid" NOT NULL,
    "factor_id" "uuid" NOT NULL,
    "created_at" timestamp with time zone NOT NULL,
    "verified_at" timestamp with time zone,
    "ip_address" "inet" NOT NULL,
    "otp_code" "text",
    "web_authn_session_data" "jsonb"
);


--
-- TOC entry 4429 (class 0 OID 0)
-- Dependencies: 338
-- Name: TABLE "mfa_challenges"; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE "auth"."mfa_challenges" IS 'auth: stores metadata about challenge requests made';


--
-- TOC entry 337 (class 1259 OID 16789)
-- Name: mfa_factors; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE "auth"."mfa_factors" (
    "id" "uuid" NOT NULL,
    "user_id" "uuid" NOT NULL,
    "friendly_name" "text",
    "factor_type" "auth"."factor_type" NOT NULL,
    "status" "auth"."factor_status" NOT NULL,
    "created_at" timestamp with time zone NOT NULL,
    "updated_at" timestamp with time zone NOT NULL,
    "secret" "text",
    "phone" "text",
    "last_challenged_at" timestamp with time zone,
    "web_authn_credential" "jsonb",
    "web_authn_aaguid" "uuid"
);


--
-- TOC entry 4430 (class 0 OID 0)
-- Dependencies: 337
-- Name: TABLE "mfa_factors"; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE "auth"."mfa_factors" IS 'auth: stores metadata about factors';


--
-- TOC entry 346 (class 1259 OID 17009)
-- Name: oauth_clients; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE "auth"."oauth_clients" (
    "id" "uuid" NOT NULL,
    "client_id" "text" NOT NULL,
    "client_secret_hash" "text" NOT NULL,
    "registration_type" "auth"."oauth_registration_type" NOT NULL,
    "redirect_uris" "text" NOT NULL,
    "grant_types" "text" NOT NULL,
    "client_name" "text",
    "client_uri" "text",
    "logo_uri" "text",
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "deleted_at" timestamp with time zone,
    CONSTRAINT "oauth_clients_client_name_length" CHECK (("char_length"("client_name") <= 1024)),
    CONSTRAINT "oauth_clients_client_uri_length" CHECK (("char_length"("client_uri") <= 2048)),
    CONSTRAINT "oauth_clients_logo_uri_length" CHECK (("char_length"("logo_uri") <= 2048))
);


--
-- TOC entry 345 (class 1259 OID 16977)
-- Name: one_time_tokens; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE "auth"."one_time_tokens" (
    "id" "uuid" NOT NULL,
    "user_id" "uuid" NOT NULL,
    "token_type" "auth"."one_time_token_type" NOT NULL,
    "token_hash" "text" NOT NULL,
    "relates_to" "text" NOT NULL,
    "created_at" timestamp without time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp without time zone DEFAULT "now"() NOT NULL,
    CONSTRAINT "one_time_tokens_token_hash_check" CHECK (("char_length"("token_hash") > 0))
);


--
-- TOC entry 325 (class 1259 OID 16507)
-- Name: refresh_tokens; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE "auth"."refresh_tokens" (
    "instance_id" "uuid",
    "id" bigint NOT NULL,
    "token" character varying(255),
    "user_id" character varying(255),
    "revoked" boolean,
    "created_at" timestamp with time zone,
    "updated_at" timestamp with time zone,
    "parent" character varying(255),
    "session_id" "uuid"
);


--
-- TOC entry 4431 (class 0 OID 0)
-- Dependencies: 325
-- Name: TABLE "refresh_tokens"; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE "auth"."refresh_tokens" IS 'Auth: Store of tokens used to refresh JWT tokens once they expire.';


--
-- TOC entry 324 (class 1259 OID 16506)
-- Name: refresh_tokens_id_seq; Type: SEQUENCE; Schema: auth; Owner: -
--

CREATE SEQUENCE "auth"."refresh_tokens_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4432 (class 0 OID 0)
-- Dependencies: 324
-- Name: refresh_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: auth; Owner: -
--

ALTER SEQUENCE "auth"."refresh_tokens_id_seq" OWNED BY "auth"."refresh_tokens"."id";


--
-- TOC entry 342 (class 1259 OID 16856)
-- Name: saml_providers; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE "auth"."saml_providers" (
    "id" "uuid" NOT NULL,
    "sso_provider_id" "uuid" NOT NULL,
    "entity_id" "text" NOT NULL,
    "metadata_xml" "text" NOT NULL,
    "metadata_url" "text",
    "attribute_mapping" "jsonb",
    "created_at" timestamp with time zone,
    "updated_at" timestamp with time zone,
    "name_id_format" "text",
    CONSTRAINT "entity_id not empty" CHECK (("char_length"("entity_id") > 0)),
    CONSTRAINT "metadata_url not empty" CHECK ((("metadata_url" = NULL::"text") OR ("char_length"("metadata_url") > 0))),
    CONSTRAINT "metadata_xml not empty" CHECK (("char_length"("metadata_xml") > 0))
);


--
-- TOC entry 4433 (class 0 OID 0)
-- Dependencies: 342
-- Name: TABLE "saml_providers"; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE "auth"."saml_providers" IS 'Auth: Manages SAML Identity Provider connections.';


--
-- TOC entry 343 (class 1259 OID 16874)
-- Name: saml_relay_states; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE "auth"."saml_relay_states" (
    "id" "uuid" NOT NULL,
    "sso_provider_id" "uuid" NOT NULL,
    "request_id" "text" NOT NULL,
    "for_email" "text",
    "redirect_to" "text",
    "created_at" timestamp with time zone,
    "updated_at" timestamp with time zone,
    "flow_state_id" "uuid",
    CONSTRAINT "request_id not empty" CHECK (("char_length"("request_id") > 0))
);


--
-- TOC entry 4434 (class 0 OID 0)
-- Dependencies: 343
-- Name: TABLE "saml_relay_states"; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE "auth"."saml_relay_states" IS 'Auth: Contains SAML Relay State information for each Service Provider initiated login.';


--
-- TOC entry 328 (class 1259 OID 16533)
-- Name: schema_migrations; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE "auth"."schema_migrations" (
    "version" character varying(255) NOT NULL
);


--
-- TOC entry 4435 (class 0 OID 0)
-- Dependencies: 328
-- Name: TABLE "schema_migrations"; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE "auth"."schema_migrations" IS 'Auth: Manages updates to the auth system.';


--
-- TOC entry 336 (class 1259 OID 16755)
-- Name: sessions; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE "auth"."sessions" (
    "id" "uuid" NOT NULL,
    "user_id" "uuid" NOT NULL,
    "created_at" timestamp with time zone,
    "updated_at" timestamp with time zone,
    "factor_id" "uuid",
    "aal" "auth"."aal_level",
    "not_after" timestamp with time zone,
    "refreshed_at" timestamp without time zone,
    "user_agent" "text",
    "ip" "inet",
    "tag" "text"
);


--
-- TOC entry 4436 (class 0 OID 0)
-- Dependencies: 336
-- Name: TABLE "sessions"; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE "auth"."sessions" IS 'Auth: Stores session data associated to a user.';


--
-- TOC entry 4437 (class 0 OID 0)
-- Dependencies: 336
-- Name: COLUMN "sessions"."not_after"; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON COLUMN "auth"."sessions"."not_after" IS 'Auth: Not after is a nullable column that contains a timestamp after which the session should be regarded as expired.';


--
-- TOC entry 341 (class 1259 OID 16841)
-- Name: sso_domains; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE "auth"."sso_domains" (
    "id" "uuid" NOT NULL,
    "sso_provider_id" "uuid" NOT NULL,
    "domain" "text" NOT NULL,
    "created_at" timestamp with time zone,
    "updated_at" timestamp with time zone,
    CONSTRAINT "domain not empty" CHECK (("char_length"("domain") > 0))
);


--
-- TOC entry 4438 (class 0 OID 0)
-- Dependencies: 341
-- Name: TABLE "sso_domains"; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE "auth"."sso_domains" IS 'Auth: Manages SSO email address domain mapping to an SSO Identity Provider.';


--
-- TOC entry 340 (class 1259 OID 16832)
-- Name: sso_providers; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE "auth"."sso_providers" (
    "id" "uuid" NOT NULL,
    "resource_id" "text",
    "created_at" timestamp with time zone,
    "updated_at" timestamp with time zone,
    "disabled" boolean,
    CONSTRAINT "resource_id not empty" CHECK ((("resource_id" = NULL::"text") OR ("char_length"("resource_id") > 0)))
);


--
-- TOC entry 4439 (class 0 OID 0)
-- Dependencies: 340
-- Name: TABLE "sso_providers"; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE "auth"."sso_providers" IS 'Auth: Manages SSO identity provider information; see saml_providers for SAML.';


--
-- TOC entry 4440 (class 0 OID 0)
-- Dependencies: 340
-- Name: COLUMN "sso_providers"."resource_id"; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON COLUMN "auth"."sso_providers"."resource_id" IS 'Auth: Uniquely identifies a SSO provider according to a user-chosen resource ID (case insensitive), useful in infrastructure as code.';


--
-- TOC entry 323 (class 1259 OID 16495)
-- Name: users; Type: TABLE; Schema: auth; Owner: -
--

CREATE TABLE "auth"."users" (
    "instance_id" "uuid",
    "id" "uuid" NOT NULL,
    "aud" character varying(255),
    "role" character varying(255),
    "email" character varying(255),
    "encrypted_password" character varying(255),
    "email_confirmed_at" timestamp with time zone,
    "invited_at" timestamp with time zone,
    "confirmation_token" character varying(255),
    "confirmation_sent_at" timestamp with time zone,
    "recovery_token" character varying(255),
    "recovery_sent_at" timestamp with time zone,
    "email_change_token_new" character varying(255),
    "email_change" character varying(255),
    "email_change_sent_at" timestamp with time zone,
    "last_sign_in_at" timestamp with time zone,
    "raw_app_meta_data" "jsonb",
    "raw_user_meta_data" "jsonb",
    "is_super_admin" boolean,
    "created_at" timestamp with time zone,
    "updated_at" timestamp with time zone,
    "phone" "text" DEFAULT NULL::character varying,
    "phone_confirmed_at" timestamp with time zone,
    "phone_change" "text" DEFAULT ''::character varying,
    "phone_change_token" character varying(255) DEFAULT ''::character varying,
    "phone_change_sent_at" timestamp with time zone,
    "confirmed_at" timestamp with time zone GENERATED ALWAYS AS (LEAST("email_confirmed_at", "phone_confirmed_at")) STORED,
    "email_change_token_current" character varying(255) DEFAULT ''::character varying,
    "email_change_confirm_status" smallint DEFAULT 0,
    "banned_until" timestamp with time zone,
    "reauthentication_token" character varying(255) DEFAULT ''::character varying,
    "reauthentication_sent_at" timestamp with time zone,
    "is_sso_user" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone,
    "is_anonymous" boolean DEFAULT false NOT NULL,
    CONSTRAINT "users_email_change_confirm_status_check" CHECK ((("email_change_confirm_status" >= 0) AND ("email_change_confirm_status" <= 2)))
);


--
-- TOC entry 4441 (class 0 OID 0)
-- Dependencies: 323
-- Name: TABLE "users"; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON TABLE "auth"."users" IS 'Auth: Stores user login data within a secure schema.';


--
-- TOC entry 4442 (class 0 OID 0)
-- Dependencies: 323
-- Name: COLUMN "users"."is_sso_user"; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON COLUMN "auth"."users"."is_sso_user" IS 'Auth: Set this column to true when the account comes from SSO. These accounts can have duplicate emails.';


--
-- TOC entry 357 (class 1259 OID 17297)
-- Name: __migrations_applied; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."__migrations_applied" (
    "id" bigint NOT NULL,
    "filename" "text" NOT NULL,
    "applied_at" timestamp with time zone DEFAULT "now"()
);


--
-- TOC entry 356 (class 1259 OID 17296)
-- Name: __migrations_applied_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."__migrations_applied_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4443 (class 0 OID 0)
-- Dependencies: 356
-- Name: __migrations_applied_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."__migrations_applied_id_seq" OWNED BY "public"."__migrations_applied"."id";


--
-- TOC entry 359 (class 1259 OID 17309)
-- Name: brand; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."brand" (
    "id" bigint NOT NULL,
    "name" "text" NOT NULL,
    "website" "text"
);


--
-- TOC entry 363 (class 1259 OID 17336)
-- Name: brand_category_map; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."brand_category_map" (
    "id" bigint NOT NULL,
    "brand_id" bigint,
    "original_label" "text" NOT NULL,
    "category_id" bigint,
    "created_at" timestamp with time zone DEFAULT "now"()
);


--
-- TOC entry 362 (class 1259 OID 17335)
-- Name: brand_category_map_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."brand_category_map_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4444 (class 0 OID 0)
-- Dependencies: 362
-- Name: brand_category_map_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."brand_category_map_id_seq" OWNED BY "public"."brand_category_map"."id";


--
-- TOC entry 371 (class 1259 OID 17389)
-- Name: brand_color_map; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."brand_color_map" (
    "id" bigint NOT NULL,
    "brand_id" bigint,
    "original" "text" NOT NULL,
    "color_id" bigint,
    "notes" "text"
);


--
-- TOC entry 370 (class 1259 OID 17388)
-- Name: brand_color_map_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."brand_color_map_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4445 (class 0 OID 0)
-- Dependencies: 370
-- Name: brand_color_map_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."brand_color_map_id_seq" OWNED BY "public"."brand_color_map"."id";


--
-- TOC entry 358 (class 1259 OID 17308)
-- Name: brand_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."brand_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4446 (class 0 OID 0)
-- Dependencies: 358
-- Name: brand_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."brand_id_seq" OWNED BY "public"."brand"."id";


--
-- TOC entry 401 (class 1259 OID 18873)
-- Name: brand_profile; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."brand_profile" (
    "id" bigint NOT NULL,
    "brand_id" bigint NOT NULL,
    "slug" "text",
    "rules" "jsonb" DEFAULT '{}'::"jsonb" NOT NULL,
    "notes_md" "text"
);


--
-- TOC entry 400 (class 1259 OID 18872)
-- Name: brand_profile_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."brand_profile_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4447 (class 0 OID 0)
-- Dependencies: 400
-- Name: brand_profile_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."brand_profile_id_seq" OWNED BY "public"."brand_profile"."id";


--
-- TOC entry 361 (class 1259 OID 17320)
-- Name: category; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."category" (
    "id" bigint NOT NULL,
    "parent_id" bigint,
    "slug" "text" NOT NULL,
    "name" "text" NOT NULL
);


--
-- TOC entry 360 (class 1259 OID 17319)
-- Name: category_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."category_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4448 (class 0 OID 0)
-- Dependencies: 360
-- Name: category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."category_id_seq" OWNED BY "public"."category"."id";


--
-- TOC entry 369 (class 1259 OID 17378)
-- Name: color_catalog; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."color_catalog" (
    "id" bigint NOT NULL,
    "canonical" "text" NOT NULL,
    "family" "text",
    "hex" "text"
);


--
-- TOC entry 368 (class 1259 OID 17377)
-- Name: color_catalog_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."color_catalog_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4449 (class 0 OID 0)
-- Dependencies: 368
-- Name: color_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."color_catalog_id_seq" OWNED BY "public"."color_catalog"."id";


--
-- TOC entry 391 (class 1259 OID 17581)
-- Name: evidence; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."evidence" (
    "id" bigint NOT NULL,
    "ingest_run_id" bigint,
    "style_id" bigint,
    "variant_id" bigint,
    "url" "text",
    "raw_blob_ref" "text",
    "captured_at" timestamp with time zone DEFAULT "now"()
);


--
-- TOC entry 390 (class 1259 OID 17580)
-- Name: evidence_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."evidence_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4450 (class 0 OID 0)
-- Dependencies: 390
-- Name: evidence_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."evidence_id_seq" OWNED BY "public"."evidence"."id";


--
-- TOC entry 365 (class 1259 OID 17356)
-- Name: fabric_catalog; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."fabric_catalog" (
    "id" bigint NOT NULL,
    "name" "text" NOT NULL,
    "composition" "text"
);


--
-- TOC entry 364 (class 1259 OID 17355)
-- Name: fabric_catalog_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."fabric_catalog_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4451 (class 0 OID 0)
-- Dependencies: 364
-- Name: fabric_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."fabric_catalog_id_seq" OWNED BY "public"."fabric_catalog"."id";


--
-- TOC entry 367 (class 1259 OID 17367)
-- Name: fit_catalog; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."fit_catalog" (
    "id" bigint NOT NULL,
    "name" "text" NOT NULL
);


--
-- TOC entry 366 (class 1259 OID 17366)
-- Name: fit_catalog_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."fit_catalog_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4452 (class 0 OID 0)
-- Dependencies: 366
-- Name: fit_catalog_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."fit_catalog_id_seq" OWNED BY "public"."fit_catalog"."id";


--
-- TOC entry 389 (class 1259 OID 17566)
-- Name: ingest_run; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."ingest_run" (
    "id" bigint NOT NULL,
    "brand_id" bigint,
    "source" "text",
    "started_at" timestamp with time zone DEFAULT "now"(),
    "finished_at" timestamp with time zone,
    "notes" "text"
);


--
-- TOC entry 388 (class 1259 OID 17565)
-- Name: ingest_run_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."ingest_run_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4453 (class 0 OID 0)
-- Dependencies: 388
-- Name: ingest_run_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."ingest_run_id_seq" OWNED BY "public"."ingest_run"."id";


--
-- TOC entry 403 (class 1259 OID 18890)
-- Name: ingestion_job; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."ingestion_job" (
    "id" bigint NOT NULL,
    "brand" "text" NOT NULL,
    "source_url" "text",
    "payload" "jsonb",
    "status" "text" DEFAULT 'queued'::"text",
    "started_at" timestamp with time zone,
    "finished_at" timestamp with time zone,
    "error" "text"
);


--
-- TOC entry 402 (class 1259 OID 18889)
-- Name: ingestion_job_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."ingestion_job_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4454 (class 0 OID 0)
-- Dependencies: 402
-- Name: ingestion_job_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."ingestion_job_id_seq" OWNED BY "public"."ingestion_job"."id";


--
-- TOC entry 385 (class 1259 OID 17533)
-- Name: inventory_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."inventory_history" (
    "id" bigint NOT NULL,
    "variant_id" bigint,
    "size_label" "text",
    "region" "text",
    "status" "text",
    "qty" integer,
    "captured_at" timestamp with time zone NOT NULL
);


--
-- TOC entry 384 (class 1259 OID 17532)
-- Name: inventory_history_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."inventory_history_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4455 (class 0 OID 0)
-- Dependencies: 384
-- Name: inventory_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."inventory_history_id_seq" OWNED BY "public"."inventory_history"."id";


--
-- TOC entry 387 (class 1259 OID 17547)
-- Name: media_asset; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."media_asset" (
    "id" bigint NOT NULL,
    "style_id" bigint,
    "variant_id" bigint,
    "type" "text",
    "url" "text" NOT NULL,
    "position" integer,
    "alt" "text"
);


--
-- TOC entry 386 (class 1259 OID 17546)
-- Name: media_asset_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."media_asset_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4456 (class 0 OID 0)
-- Dependencies: 386
-- Name: media_asset_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."media_asset_id_seq" OWNED BY "public"."media_asset"."id";


--
-- TOC entry 383 (class 1259 OID 17517)
-- Name: price_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."price_history" (
    "id" bigint NOT NULL,
    "variant_id" bigint,
    "region" "text" NOT NULL,
    "currency" "text" NOT NULL,
    "list_price" numeric(12,2),
    "sale_price" numeric(12,2),
    "captured_at" timestamp with time zone NOT NULL
);


--
-- TOC entry 382 (class 1259 OID 17516)
-- Name: price_history_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."price_history_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4457 (class 0 OID 0)
-- Dependencies: 382
-- Name: price_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."price_history_id_seq" OWNED BY "public"."price_history"."id";


--
-- TOC entry 396 (class 1259 OID 18585)
-- Name: product_image; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."product_image" (
    "id" bigint NOT NULL,
    "style_id" bigint NOT NULL,
    "variant_id" bigint,
    "region" "text" DEFAULT 'US'::"text",
    "url" "text" NOT NULL,
    "position" integer DEFAULT 0,
    "is_primary" boolean DEFAULT false,
    "color_code" "text",
    "alt" "text",
    "source" "text" DEFAULT 'scrape'::"text",
    "captured_at" timestamp with time zone DEFAULT "now"()
);


--
-- TOC entry 395 (class 1259 OID 18584)
-- Name: product_image_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."product_image_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4458 (class 0 OID 0)
-- Dependencies: 395
-- Name: product_image_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."product_image_id_seq" OWNED BY "public"."product_image"."id";


--
-- TOC entry 381 (class 1259 OID 17496)
-- Name: product_url; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."product_url" (
    "id" bigint NOT NULL,
    "style_id" bigint,
    "variant_id" bigint,
    "region" "text",
    "url" "text" NOT NULL,
    "is_current" boolean DEFAULT true,
    "seen_at" timestamp with time zone DEFAULT "now"()
);


--
-- TOC entry 380 (class 1259 OID 17495)
-- Name: product_url_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."product_url_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4459 (class 0 OID 0)
-- Dependencies: 380
-- Name: product_url_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."product_url_id_seq" OWNED BY "public"."product_url"."id";


--
-- TOC entry 373 (class 1259 OID 17408)
-- Name: style; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."style" (
    "id" bigint NOT NULL,
    "brand_id" bigint,
    "category_id" bigint,
    "name" "text" NOT NULL,
    "description" "text",
    "gender" "text",
    "lifecycle" "text",
    "created_at" timestamp with time zone DEFAULT "now"()
);


--
-- TOC entry 375 (class 1259 OID 17430)
-- Name: style_code; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."style_code" (
    "id" bigint NOT NULL,
    "style_id" bigint,
    "code" "text" NOT NULL,
    "code_type" "text" NOT NULL,
    "region" "text" DEFAULT 'ALL'::"text" NOT NULL
);


--
-- TOC entry 374 (class 1259 OID 17429)
-- Name: style_code_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."style_code_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4460 (class 0 OID 0)
-- Dependencies: 374
-- Name: style_code_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."style_code_id_seq" OWNED BY "public"."style_code"."id";


--
-- TOC entry 372 (class 1259 OID 17407)
-- Name: style_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."style_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4461 (class 0 OID 0)
-- Dependencies: 372
-- Name: style_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."style_id_seq" OWNED BY "public"."style"."id";


--
-- TOC entry 377 (class 1259 OID 17447)
-- Name: variant; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."variant" (
    "id" bigint NOT NULL,
    "style_id" bigint,
    "color_id" bigint,
    "fit_id" bigint,
    "fabric_id" bigint,
    "size_scale" "text",
    "is_active" boolean DEFAULT true,
    "attrs" "jsonb" DEFAULT '{}'::"jsonb",
    "created_at" timestamp with time zone DEFAULT "now"()
);


--
-- TOC entry 393 (class 1259 OID 17758)
-- Name: v_variant_current_url; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW "public"."v_variant_current_url" AS
 WITH "var_urls" AS (
         SELECT "product_url"."variant_id",
            "product_url"."region",
            "product_url"."url",
            "row_number"() OVER (PARTITION BY "product_url"."variant_id", "product_url"."region" ORDER BY "product_url"."is_current" DESC, "product_url"."seen_at" DESC, "product_url"."id" DESC) AS "rn"
           FROM "public"."product_url"
          WHERE ("product_url"."variant_id" IS NOT NULL)
        ), "style_urls" AS (
         SELECT "product_url"."style_id",
            "product_url"."region",
            "product_url"."url",
            "row_number"() OVER (PARTITION BY "product_url"."style_id", "product_url"."region" ORDER BY "product_url"."is_current" DESC, "product_url"."seen_at" DESC, "product_url"."id" DESC) AS "rn"
           FROM "public"."product_url"
          WHERE ("product_url"."variant_id" IS NULL)
        )
 SELECT "v"."id" AS "variant_id",
    COALESCE("vu"."region", "su"."region") AS "region",
    COALESCE("vu"."url", "su"."url") AS "url"
   FROM (("public"."variant" "v"
     LEFT JOIN "var_urls" "vu" ON ((("vu"."variant_id" = "v"."id") AND ("vu"."rn" = 1))))
     LEFT JOIN "style_urls" "su" ON ((("su"."style_id" = "v"."style_id") AND ("su"."rn" = 1))));


--
-- TOC entry 392 (class 1259 OID 17754)
-- Name: v_variant_latest_price; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW "public"."v_variant_latest_price" AS
 SELECT DISTINCT ON ("variant_id", "region") "variant_id",
    "region",
    "currency",
    "list_price",
    "sale_price",
    "captured_at"
   FROM "public"."price_history"
  ORDER BY "variant_id", "region", "captured_at" DESC;


--
-- TOC entry 379 (class 1259 OID 17479)
-- Name: variant_code; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."variant_code" (
    "id" bigint NOT NULL,
    "variant_id" bigint,
    "code" "text" NOT NULL,
    "code_type" "text" NOT NULL,
    "region" "text" DEFAULT 'ALL'::"text" NOT NULL
);


--
-- TOC entry 394 (class 1259 OID 17763)
-- Name: v_product_variants; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW "public"."v_product_variants" AS
 SELECT "b"."name" AS "brand",
    "cat"."slug" AS "category",
    "st"."id" AS "style_id",
    "st"."name" AS "style_name",
    "sc"."code" AS "style_code",
    "v"."id" AS "variant_id",
    "c"."canonical" AS "color",
    "f"."name" AS "fit",
    "fab"."name" AS "fabric",
    "v"."attrs",
    "vc"."code" AS "variant_code",
    "vp"."region",
    "vp"."currency",
    "vp"."list_price",
    "vp"."sale_price",
    "vu"."url" AS "product_url"
   FROM (((((((((("public"."variant" "v"
     JOIN "public"."style" "st" ON (("st"."id" = "v"."style_id")))
     JOIN "public"."brand" "b" ON (("b"."id" = "st"."brand_id")))
     JOIN "public"."category" "cat" ON (("cat"."id" = "st"."category_id")))
     LEFT JOIN "public"."style_code" "sc" ON (("sc"."style_id" = "st"."id")))
     LEFT JOIN "public"."color_catalog" "c" ON (("c"."id" = "v"."color_id")))
     LEFT JOIN "public"."fit_catalog" "f" ON (("f"."id" = "v"."fit_id")))
     LEFT JOIN "public"."fabric_catalog" "fab" ON (("fab"."id" = "v"."fabric_id")))
     LEFT JOIN "public"."variant_code" "vc" ON (("vc"."variant_id" = "v"."id")))
     LEFT JOIN "public"."v_variant_latest_price" "vp" ON (("vp"."variant_id" = "v"."id")))
     LEFT JOIN "public"."v_variant_current_url" "vu" ON (("vu"."variant_id" = "v"."id")));


--
-- TOC entry 397 (class 1259 OID 18610)
-- Name: v_variant_current_image; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW "public"."v_variant_current_image" AS
 WITH "pref" AS (
         SELECT COALESCE("pi"."variant_id", "v"."id") AS "v_id",
            "pi"."url",
            "row_number"() OVER (PARTITION BY COALESCE("pi"."variant_id", "v"."id") ORDER BY ("pi"."variant_id" IS NULL), (NOT "pi"."is_primary"), "pi"."position", "pi"."id") AS "rn"
           FROM (("public"."variant" "v"
             JOIN "public"."style" "s" ON (("s"."id" = "v"."style_id")))
             JOIN "public"."product_image" "pi" ON ((("pi"."style_id" = "s"."id") AND (("pi"."variant_id" = "v"."id") OR ("pi"."variant_id" IS NULL)))))
        )
 SELECT "v_id" AS "variant_id",
    "url"
   FROM "pref"
  WHERE ("rn" = 1);


--
-- TOC entry 398 (class 1259 OID 18615)
-- Name: v_product_variants_img; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW "public"."v_product_variants_img" AS
 SELECT "p"."brand",
    "p"."category",
    "p"."style_id",
    "p"."style_name",
    "p"."style_code",
    "p"."variant_id",
    "p"."color",
    "p"."fit",
    "p"."fabric",
    "p"."attrs",
    "p"."variant_code",
    "p"."region",
    "p"."currency",
    "p"."list_price",
    "p"."sale_price",
    "p"."product_url",
    "img"."url" AS "image_url"
   FROM ("public"."v_product_variants" "p"
     LEFT JOIN "public"."v_variant_current_image" "img" ON (("img"."variant_id" = "p"."variant_id")));


--
-- TOC entry 399 (class 1259 OID 18621)
-- Name: v_variants_missing_image; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW "public"."v_variants_missing_image" AS
 SELECT "v"."id" AS "variant_id",
    "b"."name" AS "brand",
    "st"."name" AS "style_name",
    "sc"."code" AS "style_code",
    "c"."canonical" AS "color",
    "f"."name" AS "fit"
   FROM (((((("public"."variant" "v"
     JOIN "public"."style" "st" ON (("st"."id" = "v"."style_id")))
     JOIN "public"."brand" "b" ON (("b"."id" = "st"."brand_id")))
     LEFT JOIN "public"."style_code" "sc" ON (("sc"."style_id" = "st"."id")))
     LEFT JOIN "public"."color_catalog" "c" ON (("c"."id" = "v"."color_id")))
     LEFT JOIN "public"."fit_catalog" "f" ON (("f"."id" = "v"."fit_id")))
     LEFT JOIN "public"."v_variant_current_image" "vi" ON (("vi"."variant_id" = "v"."id")))
  WHERE ("vi"."url" IS NULL);


--
-- TOC entry 378 (class 1259 OID 17478)
-- Name: variant_code_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."variant_code_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4462 (class 0 OID 0)
-- Dependencies: 378
-- Name: variant_code_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."variant_code_id_seq" OWNED BY "public"."variant_code"."id";


--
-- TOC entry 376 (class 1259 OID 17446)
-- Name: variant_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."variant_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4463 (class 0 OID 0)
-- Dependencies: 376
-- Name: variant_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."variant_id_seq" OWNED BY "public"."variant"."id";


--
-- TOC entry 355 (class 1259 OID 17277)
-- Name: messages; Type: TABLE; Schema: realtime; Owner: -
--

CREATE TABLE "realtime"."messages" (
    "topic" "text" NOT NULL,
    "extension" "text" NOT NULL,
    "payload" "jsonb",
    "event" "text",
    "private" boolean DEFAULT false,
    "updated_at" timestamp without time zone DEFAULT "now"() NOT NULL,
    "inserted_at" timestamp without time zone DEFAULT "now"() NOT NULL,
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL
)
PARTITION BY RANGE ("inserted_at");


--
-- TOC entry 347 (class 1259 OID 17025)
-- Name: schema_migrations; Type: TABLE; Schema: realtime; Owner: -
--

CREATE TABLE "realtime"."schema_migrations" (
    "version" bigint NOT NULL,
    "inserted_at" timestamp(0) without time zone
);


--
-- TOC entry 352 (class 1259 OID 17131)
-- Name: subscription; Type: TABLE; Schema: realtime; Owner: -
--

CREATE TABLE "realtime"."subscription" (
    "id" bigint NOT NULL,
    "subscription_id" "uuid" NOT NULL,
    "entity" "regclass" NOT NULL,
    "filters" "realtime"."user_defined_filter"[] DEFAULT '{}'::"realtime"."user_defined_filter"[] NOT NULL,
    "claims" "jsonb" NOT NULL,
    "claims_role" "regrole" GENERATED ALWAYS AS ("realtime"."to_regrole"(("claims" ->> 'role'::"text"))) STORED NOT NULL,
    "created_at" timestamp without time zone DEFAULT "timezone"('utc'::"text", "now"()) NOT NULL
);


--
-- TOC entry 351 (class 1259 OID 17130)
-- Name: subscription_id_seq; Type: SEQUENCE; Schema: realtime; Owner: -
--

ALTER TABLE "realtime"."subscription" ALTER COLUMN "id" ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME "realtime"."subscription_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- TOC entry 329 (class 1259 OID 16546)
-- Name: buckets; Type: TABLE; Schema: storage; Owner: -
--

CREATE TABLE "storage"."buckets" (
    "id" "text" NOT NULL,
    "name" "text" NOT NULL,
    "owner" "uuid",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    "public" boolean DEFAULT false,
    "avif_autodetection" boolean DEFAULT false,
    "file_size_limit" bigint,
    "allowed_mime_types" "text"[],
    "owner_id" "text",
    "type" "storage"."buckettype" DEFAULT 'STANDARD'::"storage"."buckettype" NOT NULL
);


--
-- TOC entry 4464 (class 0 OID 0)
-- Dependencies: 329
-- Name: COLUMN "buckets"."owner"; Type: COMMENT; Schema: storage; Owner: -
--

COMMENT ON COLUMN "storage"."buckets"."owner" IS 'Field is deprecated, use owner_id instead';


--
-- TOC entry 413 (class 1259 OID 43342)
-- Name: buckets_analytics; Type: TABLE; Schema: storage; Owner: -
--

CREATE TABLE "storage"."buckets_analytics" (
    "id" "text" NOT NULL,
    "type" "storage"."buckettype" DEFAULT 'ANALYTICS'::"storage"."buckettype" NOT NULL,
    "format" "text" DEFAULT 'ICEBERG'::"text" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


--
-- TOC entry 331 (class 1259 OID 16588)
-- Name: migrations; Type: TABLE; Schema: storage; Owner: -
--

CREATE TABLE "storage"."migrations" (
    "id" integer NOT NULL,
    "name" character varying(100) NOT NULL,
    "hash" character varying(40) NOT NULL,
    "executed_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- TOC entry 330 (class 1259 OID 16561)
-- Name: objects; Type: TABLE; Schema: storage; Owner: -
--

CREATE TABLE "storage"."objects" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "bucket_id" "text",
    "name" "text",
    "owner" "uuid",
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"(),
    "last_accessed_at" timestamp with time zone DEFAULT "now"(),
    "metadata" "jsonb",
    "path_tokens" "text"[] GENERATED ALWAYS AS ("string_to_array"("name", '/'::"text")) STORED,
    "version" "text",
    "owner_id" "text",
    "user_metadata" "jsonb",
    "level" integer
);


--
-- TOC entry 4465 (class 0 OID 0)
-- Dependencies: 330
-- Name: COLUMN "objects"."owner"; Type: COMMENT; Schema: storage; Owner: -
--

COMMENT ON COLUMN "storage"."objects"."owner" IS 'Field is deprecated, use owner_id instead';


--
-- TOC entry 412 (class 1259 OID 43298)
-- Name: prefixes; Type: TABLE; Schema: storage; Owner: -
--

CREATE TABLE "storage"."prefixes" (
    "bucket_id" "text" NOT NULL,
    "name" "text" NOT NULL COLLATE "pg_catalog"."C",
    "level" integer GENERATED ALWAYS AS ("storage"."get_level"("name")) STORED NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"(),
    "updated_at" timestamp with time zone DEFAULT "now"()
);


--
-- TOC entry 348 (class 1259 OID 17062)
-- Name: s3_multipart_uploads; Type: TABLE; Schema: storage; Owner: -
--

CREATE TABLE "storage"."s3_multipart_uploads" (
    "id" "text" NOT NULL,
    "in_progress_size" bigint DEFAULT 0 NOT NULL,
    "upload_signature" "text" NOT NULL,
    "bucket_id" "text" NOT NULL,
    "key" "text" NOT NULL COLLATE "pg_catalog"."C",
    "version" "text" NOT NULL,
    "owner_id" "text",
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "user_metadata" "jsonb"
);


--
-- TOC entry 349 (class 1259 OID 17076)
-- Name: s3_multipart_uploads_parts; Type: TABLE; Schema: storage; Owner: -
--

CREATE TABLE "storage"."s3_multipart_uploads_parts" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "upload_id" "text" NOT NULL,
    "size" bigint DEFAULT 0 NOT NULL,
    "part_number" integer NOT NULL,
    "bucket_id" "text" NOT NULL,
    "key" "text" NOT NULL COLLATE "pg_catalog"."C",
    "etag" "text" NOT NULL,
    "owner_id" "text",
    "version" "text" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


--
-- TOC entry 411 (class 1259 OID 23422)
-- Name: hooks; Type: TABLE; Schema: supabase_functions; Owner: -
--

CREATE TABLE "supabase_functions"."hooks" (
    "id" bigint NOT NULL,
    "hook_table_id" integer NOT NULL,
    "hook_name" "text" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "request_id" bigint
);


--
-- TOC entry 4466 (class 0 OID 0)
-- Dependencies: 411
-- Name: TABLE "hooks"; Type: COMMENT; Schema: supabase_functions; Owner: -
--

COMMENT ON TABLE "supabase_functions"."hooks" IS 'Supabase Functions Hooks: Audit trail for triggered hooks.';


--
-- TOC entry 410 (class 1259 OID 23421)
-- Name: hooks_id_seq; Type: SEQUENCE; Schema: supabase_functions; Owner: -
--

CREATE SEQUENCE "supabase_functions"."hooks_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 4467 (class 0 OID 0)
-- Dependencies: 410
-- Name: hooks_id_seq; Type: SEQUENCE OWNED BY; Schema: supabase_functions; Owner: -
--

ALTER SEQUENCE "supabase_functions"."hooks_id_seq" OWNED BY "supabase_functions"."hooks"."id";


--
-- TOC entry 409 (class 1259 OID 23413)
-- Name: migrations; Type: TABLE; Schema: supabase_functions; Owner: -
--

CREATE TABLE "supabase_functions"."migrations" (
    "version" "text" NOT NULL,
    "inserted_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


--
-- TOC entry 3798 (class 2604 OID 16510)
-- Name: refresh_tokens id; Type: DEFAULT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."refresh_tokens" ALTER COLUMN "id" SET DEFAULT "nextval"('"auth"."refresh_tokens_id_seq"'::"regclass");


--
-- TOC entry 3834 (class 2604 OID 17300)
-- Name: __migrations_applied id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."__migrations_applied" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."__migrations_applied_id_seq"'::"regclass");


--
-- TOC entry 3836 (class 2604 OID 17312)
-- Name: brand id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."brand" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."brand_id_seq"'::"regclass");


--
-- TOC entry 3838 (class 2604 OID 17339)
-- Name: brand_category_map id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."brand_category_map" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."brand_category_map_id_seq"'::"regclass");


--
-- TOC entry 3843 (class 2604 OID 17392)
-- Name: brand_color_map id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."brand_color_map" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."brand_color_map_id_seq"'::"regclass");


--
-- TOC entry 3870 (class 2604 OID 18876)
-- Name: brand_profile id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."brand_profile" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."brand_profile_id_seq"'::"regclass");


--
-- TOC entry 3837 (class 2604 OID 17323)
-- Name: category id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."category" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."category_id_seq"'::"regclass");


--
-- TOC entry 3842 (class 2604 OID 17381)
-- Name: color_catalog id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."color_catalog" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."color_catalog_id_seq"'::"regclass");


--
-- TOC entry 3862 (class 2604 OID 17584)
-- Name: evidence id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."evidence" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."evidence_id_seq"'::"regclass");


--
-- TOC entry 3840 (class 2604 OID 17359)
-- Name: fabric_catalog id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."fabric_catalog" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."fabric_catalog_id_seq"'::"regclass");


--
-- TOC entry 3841 (class 2604 OID 17370)
-- Name: fit_catalog id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."fit_catalog" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."fit_catalog_id_seq"'::"regclass");


--
-- TOC entry 3860 (class 2604 OID 17569)
-- Name: ingest_run id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."ingest_run" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."ingest_run_id_seq"'::"regclass");


--
-- TOC entry 3872 (class 2604 OID 18893)
-- Name: ingestion_job id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."ingestion_job" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."ingestion_job_id_seq"'::"regclass");


--
-- TOC entry 3858 (class 2604 OID 17536)
-- Name: inventory_history id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."inventory_history" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."inventory_history_id_seq"'::"regclass");


--
-- TOC entry 3859 (class 2604 OID 17550)
-- Name: media_asset id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."media_asset" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."media_asset_id_seq"'::"regclass");


--
-- TOC entry 3857 (class 2604 OID 17520)
-- Name: price_history id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."price_history" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."price_history_id_seq"'::"regclass");


--
-- TOC entry 3864 (class 2604 OID 18588)
-- Name: product_image id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."product_image" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."product_image_id_seq"'::"regclass");


--
-- TOC entry 3854 (class 2604 OID 17499)
-- Name: product_url id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."product_url" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."product_url_id_seq"'::"regclass");


--
-- TOC entry 3844 (class 2604 OID 17411)
-- Name: style id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."style" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."style_id_seq"'::"regclass");


--
-- TOC entry 3846 (class 2604 OID 17433)
-- Name: style_code id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."style_code" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."style_code_id_seq"'::"regclass");


--
-- TOC entry 3848 (class 2604 OID 17450)
-- Name: variant id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."variant" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."variant_id_seq"'::"regclass");


--
-- TOC entry 3852 (class 2604 OID 17482)
-- Name: variant_code id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."variant_code" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."variant_code_id_seq"'::"regclass");


--
-- TOC entry 3876 (class 2604 OID 23425)
-- Name: hooks id; Type: DEFAULT; Schema: supabase_functions; Owner: -
--

ALTER TABLE ONLY "supabase_functions"."hooks" ALTER COLUMN "id" SET DEFAULT "nextval"('"supabase_functions"."hooks_id_seq"'::"regclass");


--
-- TOC entry 4335 (class 0 OID 16525)
-- Dependencies: 327
-- Data for Name: audit_log_entries; Type: TABLE DATA; Schema: auth; Owner: -
--



--
-- TOC entry 4349 (class 0 OID 16927)
-- Dependencies: 344
-- Data for Name: flow_state; Type: TABLE DATA; Schema: auth; Owner: -
--



--
-- TOC entry 4340 (class 0 OID 16725)
-- Dependencies: 335
-- Data for Name: identities; Type: TABLE DATA; Schema: auth; Owner: -
--



--
-- TOC entry 4334 (class 0 OID 16518)
-- Dependencies: 326
-- Data for Name: instances; Type: TABLE DATA; Schema: auth; Owner: -
--



--
-- TOC entry 4344 (class 0 OID 16814)
-- Dependencies: 339
-- Data for Name: mfa_amr_claims; Type: TABLE DATA; Schema: auth; Owner: -
--



--
-- TOC entry 4343 (class 0 OID 16802)
-- Dependencies: 338
-- Data for Name: mfa_challenges; Type: TABLE DATA; Schema: auth; Owner: -
--



--
-- TOC entry 4342 (class 0 OID 16789)
-- Dependencies: 337
-- Data for Name: mfa_factors; Type: TABLE DATA; Schema: auth; Owner: -
--



--
-- TOC entry 4351 (class 0 OID 17009)
-- Dependencies: 346
-- Data for Name: oauth_clients; Type: TABLE DATA; Schema: auth; Owner: -
--



--
-- TOC entry 4350 (class 0 OID 16977)
-- Dependencies: 345
-- Data for Name: one_time_tokens; Type: TABLE DATA; Schema: auth; Owner: -
--



--
-- TOC entry 4333 (class 0 OID 16507)
-- Dependencies: 325
-- Data for Name: refresh_tokens; Type: TABLE DATA; Schema: auth; Owner: -
--



--
-- TOC entry 4347 (class 0 OID 16856)
-- Dependencies: 342
-- Data for Name: saml_providers; Type: TABLE DATA; Schema: auth; Owner: -
--



--
-- TOC entry 4348 (class 0 OID 16874)
-- Dependencies: 343
-- Data for Name: saml_relay_states; Type: TABLE DATA; Schema: auth; Owner: -
--



--
-- TOC entry 4336 (class 0 OID 16533)
-- Dependencies: 328
-- Data for Name: schema_migrations; Type: TABLE DATA; Schema: auth; Owner: -
--

INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20171026211738');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20171026211808');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20171026211834');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20180103212743');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20180108183307');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20180119214651');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20180125194653');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('00');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20210710035447');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20210722035447');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20210730183235');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20210909172000');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20210927181326');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20211122151130');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20211124214934');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20211202183645');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20220114185221');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20220114185340');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20220224000811');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20220323170000');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20220429102000');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20220531120530');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20220614074223');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20220811173540');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20221003041349');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20221003041400');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20221011041400');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20221020193600');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20221021073300');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20221021082433');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20221027105023');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20221114143122');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20221114143410');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20221125140132');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20221208132122');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20221215195500');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20221215195800');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20221215195900');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20230116124310');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20230116124412');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20230131181311');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20230322519590');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20230402418590');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20230411005111');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20230508135423');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20230523124323');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20230818113222');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20230914180801');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20231027141322');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20231114161723');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20231117164230');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20240115144230');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20240214120130');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20240306115329');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20240314092811');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20240427152123');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20240612123726');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20240729123726');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20240802193726');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20240806073726');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20241009103726');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20250717082212');
INSERT INTO "auth"."schema_migrations" ("version") VALUES ('20250731150234');


--
-- TOC entry 4341 (class 0 OID 16755)
-- Dependencies: 336
-- Data for Name: sessions; Type: TABLE DATA; Schema: auth; Owner: -
--



--
-- TOC entry 4346 (class 0 OID 16841)
-- Dependencies: 341
-- Data for Name: sso_domains; Type: TABLE DATA; Schema: auth; Owner: -
--



--
-- TOC entry 4345 (class 0 OID 16832)
-- Dependencies: 340
-- Data for Name: sso_providers; Type: TABLE DATA; Schema: auth; Owner: -
--



--
-- TOC entry 4331 (class 0 OID 16495)
-- Dependencies: 323
-- Data for Name: users; Type: TABLE DATA; Schema: auth; Owner: -
--



--
-- TOC entry 4358 (class 0 OID 17297)
-- Dependencies: 357
-- Data for Name: __migrations_applied; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO "public"."__migrations_applied" ("id", "filename", "applied_at") VALUES (1, '001_init_schema.sql', '2025-09-19 00:51:04.664547+00');
INSERT INTO "public"."__migrations_applied" ("id", "filename", "applied_at") VALUES (2, '002_seed_conversation_data.sql', '2025-09-19 00:54:53.819276+00');
INSERT INTO "public"."__migrations_applied" ("id", "filename", "applied_at") VALUES (3, '003_seed_reiss_variants.sql', '2025-09-19 01:03:54.334073+00');
INSERT INTO "public"."__migrations_applied" ("id", "filename", "applied_at") VALUES (4, '004_app_views.sql', '2025-09-19 01:05:27.140345+00');
INSERT INTO "public"."__migrations_applied" ("id", "filename", "applied_at") VALUES (5, '005_backfill_reiss_prices.sql', '2025-09-19 01:08:40.419417+00');
INSERT INTO "public"."__migrations_applied" ("id", "filename", "applied_at") VALUES (6, '006_view_url_fallback.sql', '2025-09-19 01:10:56.136981+00');
INSERT INTO "public"."__migrations_applied" ("id", "filename", "applied_at") VALUES (7, '007_style_urls.sql', '2025-09-19 01:24:41.873246+00');
INSERT INTO "public"."__migrations_applied" ("id", "filename", "applied_at") VALUES (8, '008_backfill_urls_theory_aritzia_reiss.sql', '2025-09-19 01:29:45.691581+00');
INSERT INTO "public"."__migrations_applied" ("id", "filename", "applied_at") VALUES (9, '009_upsert_api.sql', '2025-09-19 02:52:41.598443+00');
INSERT INTO "public"."__migrations_applied" ("id", "filename", "applied_at") VALUES (10, '010_dedupe_brand_color_map.sql', '2025-09-19 02:57:01.862699+00');
INSERT INTO "public"."__migrations_applied" ("id", "filename", "applied_at") VALUES (11, '011_update_upsert_variant.sql', '2025-09-19 03:02:27.386346+00');
INSERT INTO "public"."__migrations_applied" ("id", "filename", "applied_at") VALUES (12, '012_price_snapshot_babaton_eyecatcher.sql', '2025-09-19 03:02:27.628287+00');
INSERT INTO "public"."__migrations_applied" ("id", "filename", "applied_at") VALUES (13, '013_product_images.sql', '2025-09-19 04:14:21.857638+00');
INSERT INTO "public"."__migrations_applied" ("id", "filename", "applied_at") VALUES (14, '014_upsert_variant_images.sql', '2025-09-19 04:16:47.226808+00');
INSERT INTO "public"."__migrations_applied" ("id", "filename", "applied_at") VALUES (15, '015_brand_profiles.sql', '2025-09-19 04:40:31.998116+00');
INSERT INTO "public"."__migrations_applied" ("id", "filename", "applied_at") VALUES (16, '016_job_queue.sql', '2025-09-19 04:40:32.189668+00');


--
-- TOC entry 4360 (class 0 OID 17309)
-- Dependencies: 359
-- Data for Name: brand; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO "public"."brand" ("id", "name", "website") VALUES (8, 'Theory', 'https://www.theory.com');
INSERT INTO "public"."brand" ("id", "name", "website") VALUES (10, 'Aritzia', 'https://www.aritzia.com');
INSERT INTO "public"."brand" ("id", "name", "website") VALUES (6, 'Reiss', 'https://www.reiss.com');
INSERT INTO "public"."brand" ("id", "name", "website") VALUES (9, 'Babaton', 'https://www.aritzia.com');
INSERT INTO "public"."brand" ("id", "name", "website") VALUES (7, 'J.Crew', 'https://www.jcrew.com');


--
-- TOC entry 4364 (class 0 OID 17336)
-- Dependencies: 363
-- Data for Name: brand_category_map; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 4372 (class 0 OID 17389)
-- Dependencies: 371
-- Data for Name: brand_color_map; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (26, 6, 'Soft Blue', 25, NULL);
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (27, 6, 'Stone', 24, NULL);
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (28, 6, 'Rust', 26, NULL);
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (29, 6, 'Navy', 27, NULL);
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (30, 6, 'White', 28, NULL);
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (31, 6, 'Black', 29, NULL);
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (32, 6, 'Pink', 30, NULL);
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (33, 6, 'Mid Blue', 31, NULL);
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (34, 7, 'tim white blue', 33, NULL);
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (35, 7, 'ryan-gray-white', 32, NULL);
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (36, 7, 'soft-blue-oxford', 25, NULL);
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (37, 7, 'lilac-oxford', 34, NULL);
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (38, 8, 'Deep Black', 38, NULL);
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (39, 8, 'Medium Charcoal', 39, NULL);
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (40, 8, 'Ash', 40, NULL);
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (41, 8, 'Rainstorm', 41, NULL);
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (42, 8, 'Pestle', 42, NULL);
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (43, 8, 'Eclipse', 43, NULL);
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (44, 8, 'Dark Wash', 44, NULL);
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (45, 8, 'Black', 29, NULL);
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (46, 9, 'White', 28, 'Essential Colors');
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (47, 9, 'Bright White', 35, 'Limited Edition');
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (48, 9, 'Dreamhouse Pink', 36, 'Limited Edition');
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (49, 10, 'Black', 29, 'Essential Colors');
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (50, 10, 'Dayflower Blue', 37, 'Limited Edition');
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (52, 7, 'Tim White Blue', 33, NULL);
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (56, 7, 'Dark Azure', 50, NULL);
INSERT INTO "public"."brand_color_map" ("id", "brand_id", "original", "color_id", "notes") VALUES (58, 7, 'Default', 52, NULL);


--
-- TOC entry 4396 (class 0 OID 18873)
-- Dependencies: 401
-- Data for Name: brand_profile; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO "public"."brand_profile" ("id", "brand_id", "slug", "rules", "notes_md") VALUES (1, 7, 'jcrew', '{"fit_codes": {"Slim": "item_code", "Tall": "item_code", "Classic": "item_code"}, "variant_url": "style_level", "price_source": "page_state", "derived_fields": {"fabric": "Cotton-Cashmere"}, "color_code_source": "colorsList[*].colors[*].code", "style_code_source": "url_segment"}', 'J.Crew: BX291/CP682 patterns; use item codes per fit; colors from colorsList.');


--
-- TOC entry 4362 (class 0 OID 17320)
-- Dependencies: 361
-- Data for Name: category; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO "public"."category" ("id", "parent_id", "slug", "name") VALUES (5, NULL, 'shirts', 'Shirts');
INSERT INTO "public"."category" ("id", "parent_id", "slug", "name") VALUES (6, NULL, 'jackets', 'Jackets');
INSERT INTO "public"."category" ("id", "parent_id", "slug", "name") VALUES (7, NULL, 'blazers', 'Blazers');
INSERT INTO "public"."category" ("id", "parent_id", "slug", "name") VALUES (8, NULL, 'dresses', 'Dresses');
INSERT INTO "public"."category" ("id", "parent_id", "slug", "name") VALUES (16, NULL, 'dress-shirts', 'Dress-Shirts');


--
-- TOC entry 4370 (class 0 OID 17378)
-- Dependencies: 369
-- Data for Name: color_catalog; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (23, 'Bright Blue', 'Blue', NULL);
INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (24, 'Stone', 'Beige', NULL);
INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (25, 'Soft Blue', 'Blue', NULL);
INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (26, 'Rust', 'Brown', NULL);
INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (27, 'Navy', 'Blue', NULL);
INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (28, 'White', 'White', NULL);
INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (29, 'Black', 'Black', NULL);
INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (30, 'Pink', 'Pink', NULL);
INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (31, 'Mid Blue', 'Blue', NULL);
INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (32, 'Ryan Gray White', 'Grey', NULL);
INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (33, 'Tim White Blue', 'Blue', NULL);
INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (34, 'Lilac Oxford', 'Purple', NULL);
INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (35, 'Bright White', 'White', NULL);
INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (36, 'Dreamhouse Pink', 'Pink', NULL);
INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (37, 'Dayflower Blue', 'Blue', NULL);
INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (38, 'Deep Black', 'Black', NULL);
INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (39, 'Medium Charcoal', 'Grey', NULL);
INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (40, 'Ash', 'Grey', NULL);
INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (41, 'Rainstorm', 'Blue', NULL);
INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (42, 'Pestle', 'Grey', NULL);
INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (43, 'Eclipse', 'Navy', NULL);
INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (44, 'Dark Wash', 'Blue', NULL);
INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (50, 'Dark Azure', NULL, NULL);
INSERT INTO "public"."color_catalog" ("id", "canonical", "family", "hex") VALUES (52, 'Default', NULL, NULL);


--
-- TOC entry 4392 (class 0 OID 17581)
-- Dependencies: 391
-- Data for Name: evidence; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 4366 (class 0 OID 17356)
-- Dependencies: 365
-- Data for Name: fabric_catalog; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO "public"."fabric_catalog" ("id", "name", "composition") VALUES (11, 'Structure Knit', NULL);
INSERT INTO "public"."fabric_catalog" ("id", "name", "composition") VALUES (12, 'Good Cotton', NULL);
INSERT INTO "public"."fabric_catalog" ("id", "name", "composition") VALUES (13, 'Structure Twill', NULL);
INSERT INTO "public"."fabric_catalog" ("id", "name", "composition") VALUES (14, 'Summer Denim', NULL);
INSERT INTO "public"."fabric_catalog" ("id", "name", "composition") VALUES (15, 'Cotton Blend', NULL);
INSERT INTO "public"."fabric_catalog" ("id", "name", "composition") VALUES (16, 'Sateen', NULL);
INSERT INTO "public"."fabric_catalog" ("id", "name", "composition") VALUES (17, 'FigureKnit', NULL);
INSERT INTO "public"."fabric_catalog" ("id", "name", "composition") VALUES (18, 'Contour', NULL);
INSERT INTO "public"."fabric_catalog" ("id", "name", "composition") VALUES (19, 'Stretch Wool', NULL);
INSERT INTO "public"."fabric_catalog" ("id", "name", "composition") VALUES (20, 'Corduroy', NULL);
INSERT INTO "public"."fabric_catalog" ("id", "name", "composition") VALUES (24, 'Cotton-Cashmere', NULL);


--
-- TOC entry 4368 (class 0 OID 17367)
-- Dependencies: 367
-- Data for Name: fit_catalog; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO "public"."fit_catalog" ("id", "name") VALUES (5, 'Classic');
INSERT INTO "public"."fit_catalog" ("id", "name") VALUES (6, 'Slim');
INSERT INTO "public"."fit_catalog" ("id", "name") VALUES (7, 'Tall');
INSERT INTO "public"."fit_catalog" ("id", "name") VALUES (8, 'Regular');


--
-- TOC entry 4390 (class 0 OID 17566)
-- Dependencies: 389
-- Data for Name: ingest_run; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 4398 (class 0 OID 18890)
-- Dependencies: 403
-- Data for Name: ingestion_job; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 4386 (class 0 OID 17533)
-- Dependencies: 385
-- Data for Name: inventory_history; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 4388 (class 0 OID 17547)
-- Dependencies: 387
-- Data for Name: media_asset; Type: TABLE DATA; Schema: public; Owner: -
--



--
-- TOC entry 4384 (class 0 OID 17517)
-- Dependencies: 383
-- Data for Name: price_history; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO "public"."price_history" ("id", "variant_id", "region", "currency", "list_price", "sale_price", "captured_at") VALUES (3, 27, 'US', 'USD', 625.00, 468.75, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."price_history" ("id", "variant_id", "region", "currency", "list_price", "sale_price", "captured_at") VALUES (4, 28, 'US', 'USD', 625.00, 468.75, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."price_history" ("id", "variant_id", "region", "currency", "list_price", "sale_price", "captured_at") VALUES (5, 39, 'US', 'USD', 148.00, 148.00, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."price_history" ("id", "variant_id", "region", "currency", "list_price", "sale_price", "captured_at") VALUES (6, 40, 'US', 'USD', 148.00, 148.00, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."price_history" ("id", "variant_id", "region", "currency", "list_price", "sale_price", "captured_at") VALUES (7, 41, 'US', 'USD', 148.00, 148.00, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."price_history" ("id", "variant_id", "region", "currency", "list_price", "sale_price", "captured_at") VALUES (8, 42, 'US', 'USD', 128.00, 128.00, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."price_history" ("id", "variant_id", "region", "currency", "list_price", "sale_price", "captured_at") VALUES (9, 43, 'US', 'USD', 128.00, 128.00, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."price_history" ("id", "variant_id", "region", "currency", "list_price", "sale_price", "captured_at") VALUES (10, 44, 'US', 'USD', 78.00, 78.00, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."price_history" ("id", "variant_id", "region", "currency", "list_price", "sale_price", "captured_at") VALUES (11, 45, 'US', 'USD', 78.00, 78.00, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."price_history" ("id", "variant_id", "region", "currency", "list_price", "sale_price", "captured_at") VALUES (12, 46, 'US', 'USD', 98.00, 98.00, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."price_history" ("id", "variant_id", "region", "currency", "list_price", "sale_price", "captured_at") VALUES (13, 47, 'US', 'USD', 78.00, 78.00, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."price_history" ("id", "variant_id", "region", "currency", "list_price", "sale_price", "captured_at") VALUES (14, 54, 'US', 'USD', 220.00, 220.00, '2025-09-19 01:08:40.419417+00');
INSERT INTO "public"."price_history" ("id", "variant_id", "region", "currency", "list_price", "sale_price", "captured_at") VALUES (15, 55, 'US', 'USD', 220.00, 220.00, '2025-09-19 01:08:40.419417+00');
INSERT INTO "public"."price_history" ("id", "variant_id", "region", "currency", "list_price", "sale_price", "captured_at") VALUES (16, 56, 'US', 'USD', 220.00, 220.00, '2025-09-19 01:08:40.419417+00');
INSERT INTO "public"."price_history" ("id", "variant_id", "region", "currency", "list_price", "sale_price", "captured_at") VALUES (17, 57, 'US', 'USD', 220.00, 220.00, '2025-09-19 01:08:40.419417+00');
INSERT INTO "public"."price_history" ("id", "variant_id", "region", "currency", "list_price", "sale_price", "captured_at") VALUES (18, 54, 'US', 'USD', 220.00, 220.00, '2025-09-19 02:53:02.701004+00');
INSERT INTO "public"."price_history" ("id", "variant_id", "region", "currency", "list_price", "sale_price", "captured_at") VALUES (19, 60, 'US', 'USD', 148.00, 119.50, '2025-09-19 03:29:02.268695+00');
INSERT INTO "public"."price_history" ("id", "variant_id", "region", "currency", "list_price", "sale_price", "captured_at") VALUES (20, 62, 'US', 'USD', NULL, NULL, '2025-09-19 04:45:37.930385+00');


--
-- TOC entry 4394 (class 0 OID 18585)
-- Dependencies: 396
-- Data for Name: product_image; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO "public"."product_image" ("id", "style_id", "variant_id", "region", "url", "position", "is_primary", "color_code", "alt", "source", "captured_at") VALUES (1, 30, NULL, 'US', 'https://assets.aritzia.com/image/upload/c_crop,ar_1920:2623,g_south/q_auto,f_auto,dpr_auto,w_1500/f25_a08_118760_34880_on_a', 0, true, NULL, NULL, 'scrape', '2025-09-19 04:27:06.163599+00');


--
-- TOC entry 4382 (class 0 OID 17496)
-- Dependencies: 381
-- Data for Name: product_url; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (1, 18, 21, 'US', 'https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/tech-bowery/bowery-performance-stretch-oxford-shirt-with-button-down-collar/CP682?display=standard&fit=Classic&colorProductCode=CP682&color_name=tim-white-blue', true, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (2, 18, 22, 'US', 'https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/tech-bowery/bowery-performance-stretch-oxford-shirt-with-button-down-collar/CP682?display=standard&fit=Slim&colorProductCode=CP682&color_name=tim-white-blue', true, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (3, 18, 23, 'US', 'https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/tech-bowery/bowery-performance-stretch-oxford-shirt-with-button-down-collar/CP682?display=standard&fit=Tall&colorProductCode=CP682&color_name=tim-white-blue', true, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (4, 20, 27, 'US', 'https://www.theory.com/men/blazers-and-jackets/chambers-blazer-in-stretch-wool/I0171104_G0F.html', true, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (5, 20, 28, 'US', 'https://www.theory.com/men/blazers-and-jackets/chambers-blazer-in-stretch-wool/I0171104_G0F.html', true, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (6, 27, NULL, 'US', 'https://www.aritzia.com/us/en/product/figureknit%E2%84%A2-eyecatcher-dress/109178.html', true, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (7, 27, 39, 'US', 'https://www.aritzia.com/us/en/product/figureknit%E2%84%A2-eyecatcher-dress/109178.html?color=1275', true, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (8, 27, 40, 'US', 'https://www.aritzia.com/us/en/product/figureknit%E2%84%A2-eyecatcher-dress/109178.html?color=14396', true, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (9, 27, 41, 'US', 'https://www.aritzia.com/us/en/product/figureknit%E2%84%A2-eyecatcher-dress/109178.html?color=32383', true, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (10, 14, 51, 'UK', 'https://www.reiss.com/style/su422501/e71002#e71002', true, '2025-09-19 01:03:54.334073+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (11, 14, 52, 'UK', 'https://www.reiss.com/style/su422501/e70998', true, '2025-09-19 01:03:54.334073+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (12, 14, 53, 'UK', 'https://www.reiss.com/style/su422501/ab2005', true, '2025-09-19 01:03:54.334073+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (13, 15, 54, 'US', 'https://www.reiss.com/us/en/style/su538118/f18169', true, '2025-09-19 01:03:54.334073+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (14, 15, 55, 'US', 'https://www.reiss.com/us/en/style/su538118/aw1262', true, '2025-09-19 01:03:54.334073+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (15, 15, 56, 'US', 'https://www.reiss.com/us/en/style/su538118/f18163', true, '2025-09-19 01:03:54.334073+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (16, 15, 57, 'US', 'https://www.reiss.com/us/en/style/su538118/f18205', true, '2025-09-19 01:03:54.334073+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (17, 17, 20, 'UK', 'https://www.reiss.com/style/su936297/ap6308#ap6308', true, '2025-09-19 01:03:54.334073+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (18, 18, NULL, 'US', 'https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/tech-bowery/bowery-performance-stretch-oxford-shirt-with-button-down-collar/CP682?display=standard&fit=Classic&color_name=white&colorProductCode=CP682', true, '2025-09-19 01:24:41.873246+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (19, 19, NULL, 'US', 'https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/business-casual-shirts/slim-bowery-performance-stretch-dress-shirt-with-spread-collar/BX291?display=standard&fit=Classic&colorProductCode=BX291&color_name=ryan-gray-white', true, '2025-09-19 01:24:41.873246+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (20, 21, NULL, 'US', 'https://www.theory.com/men/shirts/sylvain-shirt-in-structure-knit/J0794505.html', true, '2025-09-19 01:29:45.691581+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (21, 22, NULL, 'US', 'https://www.theory.com/men/shirts/sylvain-shirt-in-good-cotton/A0674535.html', true, '2025-09-19 01:29:45.691581+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (22, 23, NULL, 'US', 'https://www.theory.com/men/shirts/sylvain-shirt-in-structure-twill/P0794514.html', true, '2025-09-19 01:29:45.691581+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (23, 24, NULL, 'US', 'https://www.theory.com/men/shirts/button-up-shirt-in-textured-check/P0774503.html', true, '2025-09-19 01:29:45.691581+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (24, 25, NULL, 'US', 'https://www.theory.com/men/shirts/noll-short-sleeve-shirt-in-summer-denim/P0574502.html', true, '2025-09-19 01:29:45.691581+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (25, 26, NULL, 'US', 'https://www.theory.com/men/shirts/noll-short-sleeve-shirt-in-cotton-blend/P0574506.html', true, '2025-09-19 01:29:45.691581+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (26, 20, NULL, 'US', 'https://www.theory.com/men/blazers-and-jackets/chambers-blazer-in-stretch-wool/I0171104.html', true, '2025-09-19 01:29:45.691581+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (27, 28, NULL, 'US', 'https://www.aritzia.com/us/en/product/figureknit%E2%84%A2-eyecatcher-mini-dress/121483.html', true, '2025-09-19 01:29:45.691581+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (28, 29, NULL, 'US', 'https://www.aritzia.com/us/en/product/original-contour-ravish-dress/123919.html', true, '2025-09-19 01:29:45.691581+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (29, 30, NULL, 'US', 'https://www.aritzia.com/us/en/product/original-contour-maxi-tube-dress/118760.html', true, '2025-09-19 01:29:45.691581+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (30, 31, NULL, 'US', 'https://www.aritzia.com/us/en/product/original-contour-mini-tube-dress/118308.html', true, '2025-09-19 01:29:45.691581+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (31, 16, 59, 'US', 'https://www.reiss.com/us/en/style/su615998/f77495', true, '2025-09-19 01:29:45.691581+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (32, 16, 58, 'US', 'https://www.reiss.com/us/en/style/su615998/f78985', true, '2025-09-19 01:29:45.691581+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (33, 15, 54, 'US', 'https://www.reiss.com/us/en/style/su538118/f18169', true, '2025-09-19 02:53:02.701004+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (34, 18, NULL, 'US', 'https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/tech-bowery/bowery-performance-stretch-oxford-shirt-with-button-down-collar/CP682?display=standard&fit=Slim&color_name=tim-white-blue&colorProductCode=CP682', true, '2025-09-19 02:53:16.694427+00');
INSERT INTO "public"."product_url" ("id", "style_id", "variant_id", "region", "url", "is_current", "seen_at") VALUES (35, 37, NULL, 'US', 'https://www.jcrew.com/p/mens/categories/clothing/shirts/cotton-cashmere/cotton-cashmere-blend-shirt/ME053?display=standard&fit=Classic&color_name=dark-azure&colorProductCode=CC100', true, '2025-09-19 03:29:02.268695+00');


--
-- TOC entry 4374 (class 0 OID 17408)
-- Dependencies: 373
-- Data for Name: style; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO "public"."style" ("id", "brand_id", "category_id", "name", "description", "gender", "lifecycle", "created_at") VALUES (14, 6, 5, 'Tucci Corduroy Overshirt', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."style" ("id", "brand_id", "category_id", "name", "description", "gender", "lifecycle", "created_at") VALUES (16, 6, 5, 'Remote Bengal Shirt', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."style" ("id", "brand_id", "category_id", "name", "description", "gender", "lifecycle", "created_at") VALUES (17, 6, 5, 'Ruban Linen Button-Through Shirt', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."style" ("id", "brand_id", "category_id", "name", "description", "gender", "lifecycle", "created_at") VALUES (19, 7, 5, 'Bowery Performance Stretch Dress Shirt with Spread Collar', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."style" ("id", "brand_id", "category_id", "name", "description", "gender", "lifecycle", "created_at") VALUES (20, 8, 7, 'Chambers Blazer in Stretch Wool', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."style" ("id", "brand_id", "category_id", "name", "description", "gender", "lifecycle", "created_at") VALUES (21, 8, 5, 'Sylvain Shirt in Structure Knit', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."style" ("id", "brand_id", "category_id", "name", "description", "gender", "lifecycle", "created_at") VALUES (22, 8, 5, 'Sylvain Shirt in Good Cotton', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."style" ("id", "brand_id", "category_id", "name", "description", "gender", "lifecycle", "created_at") VALUES (23, 8, 5, 'Sylvain Shirt in Structure Twill', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."style" ("id", "brand_id", "category_id", "name", "description", "gender", "lifecycle", "created_at") VALUES (24, 8, 5, 'Button-Up Shirt in Textured Check', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."style" ("id", "brand_id", "category_id", "name", "description", "gender", "lifecycle", "created_at") VALUES (25, 8, 5, 'Noll Short-Sleeve Shirt in Summer Denim', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."style" ("id", "brand_id", "category_id", "name", "description", "gender", "lifecycle", "created_at") VALUES (26, 8, 5, 'Noll Short-Sleeve Shirt in Cotton-Blend', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."style" ("id", "brand_id", "category_id", "name", "description", "gender", "lifecycle", "created_at") VALUES (28, 9, 8, 'FigureKnit Eyecatcher Mini Dress', NULL, 'Women', NULL, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."style" ("id", "brand_id", "category_id", "name", "description", "gender", "lifecycle", "created_at") VALUES (29, 10, 8, 'Original Contour Ravish Dress', NULL, 'Women', NULL, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."style" ("id", "brand_id", "category_id", "name", "description", "gender", "lifecycle", "created_at") VALUES (30, 10, 8, 'Original Contour Maxi Tube Dress', NULL, 'Women', NULL, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."style" ("id", "brand_id", "category_id", "name", "description", "gender", "lifecycle", "created_at") VALUES (31, 10, 8, 'Original Contour Mini Tube Dress', NULL, 'Women', NULL, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."style" ("id", "brand_id", "category_id", "name", "description", "gender", "lifecycle", "created_at") VALUES (15, 6, 5, 'Voyager Long-Sleeve Travel Shirt', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."style" ("id", "brand_id", "category_id", "name", "description", "gender", "lifecycle", "created_at") VALUES (18, 7, 5, 'Bowery Performance Stretch Oxford Shirt with Button-Down Collar', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."style" ("id", "brand_id", "category_id", "name", "description", "gender", "lifecycle", "created_at") VALUES (27, 9, 8, 'FigureKnit Eyecatcher Dress', NULL, 'Women', NULL, '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."style" ("id", "brand_id", "category_id", "name", "description", "gender", "lifecycle", "created_at") VALUES (37, 7, 5, 'Cotton-cashmere blend shirt', NULL, 'Men', NULL, '2025-09-19 03:29:02.268695+00');
INSERT INTO "public"."style" ("id", "brand_id", "category_id", "name", "description", "gender", "lifecycle", "created_at") VALUES (39, 7, 16, 'Unknown Product', NULL, 'Men', NULL, '2025-09-19 04:45:37.930385+00');


--
-- TOC entry 4376 (class 0 OID 17430)
-- Dependencies: 375
-- Data for Name: style_code; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO "public"."style_code" ("id", "style_id", "code", "code_type", "region") VALUES (14, 14, 'su422501', 'style_code', 'ALL');
INSERT INTO "public"."style_code" ("id", "style_id", "code", "code_type", "region") VALUES (15, 15, 'su538118', 'style_code', 'ALL');
INSERT INTO "public"."style_code" ("id", "style_id", "code", "code_type", "region") VALUES (16, 16, 'su615998', 'style_code', 'ALL');
INSERT INTO "public"."style_code" ("id", "style_id", "code", "code_type", "region") VALUES (17, 17, 'su936297', 'style_code', 'ALL');
INSERT INTO "public"."style_code" ("id", "style_id", "code", "code_type", "region") VALUES (18, 18, 'CP682', 'item_code', 'ALL');
INSERT INTO "public"."style_code" ("id", "style_id", "code", "code_type", "region") VALUES (19, 19, 'BX291', 'item_code', 'ALL');
INSERT INTO "public"."style_code" ("id", "style_id", "code", "code_type", "region") VALUES (20, 20, 'I0171104', 'style_code', 'ALL');
INSERT INTO "public"."style_code" ("id", "style_id", "code", "code_type", "region") VALUES (21, 21, 'J0794505', 'style_code', 'ALL');
INSERT INTO "public"."style_code" ("id", "style_id", "code", "code_type", "region") VALUES (22, 22, 'A0674535', 'style_code', 'ALL');
INSERT INTO "public"."style_code" ("id", "style_id", "code", "code_type", "region") VALUES (23, 23, 'P0794514', 'style_code', 'ALL');
INSERT INTO "public"."style_code" ("id", "style_id", "code", "code_type", "region") VALUES (24, 24, 'P0774503', 'style_code', 'ALL');
INSERT INTO "public"."style_code" ("id", "style_id", "code", "code_type", "region") VALUES (25, 25, 'P0574502', 'style_code', 'ALL');
INSERT INTO "public"."style_code" ("id", "style_id", "code", "code_type", "region") VALUES (26, 26, 'P0574506', 'style_code', 'ALL');
INSERT INTO "public"."style_code" ("id", "style_id", "code", "code_type", "region") VALUES (27, 27, '109178', 'style_code', 'ALL');
INSERT INTO "public"."style_code" ("id", "style_id", "code", "code_type", "region") VALUES (28, 28, '121483', 'style_code', 'ALL');
INSERT INTO "public"."style_code" ("id", "style_id", "code", "code_type", "region") VALUES (29, 29, '123919', 'style_code', 'ALL');
INSERT INTO "public"."style_code" ("id", "style_id", "code", "code_type", "region") VALUES (30, 30, '118760', 'style_code', 'ALL');
INSERT INTO "public"."style_code" ("id", "style_id", "code", "code_type", "region") VALUES (31, 31, '118308', 'style_code', 'ALL');
INSERT INTO "public"."style_code" ("id", "style_id", "code", "code_type", "region") VALUES (37, 37, 'ME053', 'item_code', 'ALL');
INSERT INTO "public"."style_code" ("id", "style_id", "code", "code_type", "region") VALUES (39, 39, 'BX291', 'style_code', 'ALL');


--
-- TOC entry 4378 (class 0 OID 17447)
-- Dependencies: 377
-- Data for Name: variant; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (20, 17, 23, NULL, NULL, NULL, true, '{}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (21, 18, 33, 5, NULL, NULL, true, '{}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (22, 18, 33, 6, NULL, NULL, true, '{}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (23, 18, 33, 7, NULL, NULL, true, '{}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (24, 19, 32, 5, NULL, NULL, true, '{}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (25, 19, 32, 6, NULL, NULL, true, '{}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (26, 19, 32, 7, NULL, NULL, true, '{}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (27, 20, 38, NULL, 19, NULL, true, '{}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (28, 20, 39, NULL, 19, NULL, true, '{}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (29, 21, 29, NULL, 11, NULL, true, '{}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (30, 21, 41, NULL, 11, NULL, true, '{}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (31, 21, 42, NULL, 11, NULL, true, '{}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (32, 21, 43, NULL, 11, NULL, true, '{}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (33, 22, 29, NULL, 12, NULL, true, '{}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (34, 23, 40, NULL, 13, NULL, true, '{}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (35, 24, 29, NULL, NULL, NULL, true, '{}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (36, 24, 39, NULL, NULL, NULL, true, '{}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (37, 25, 44, NULL, 14, NULL, true, '{}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (38, 26, 29, NULL, 15, NULL, true, '{}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (39, 27, 28, NULL, 17, NULL, true, '{"color_program": "Essential"}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (41, 27, 36, NULL, 17, NULL, true, '{"color_program": "Limited Edition"}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (42, 28, 29, NULL, 17, NULL, true, '{"color_program": "Essential"}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (43, 28, 35, NULL, 17, NULL, true, '{"color_program": "Limited Edition"}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (44, 29, 29, NULL, 18, NULL, true, '{"color_program": "Essential"}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (45, 29, 37, NULL, 18, NULL, true, '{"color_program": "Limited Edition"}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (46, 30, 37, NULL, 18, NULL, true, '{"color_program": "Limited Edition"}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (47, 31, 29, NULL, 18, NULL, true, '{"color_program": "Essential"}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (51, 14, 24, NULL, 20, NULL, true, '{}', '2025-09-19 01:03:54.334073+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (52, 14, 25, NULL, 20, NULL, true, '{}', '2025-09-19 01:03:54.334073+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (53, 14, 26, NULL, 20, NULL, true, '{}', '2025-09-19 01:03:54.334073+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (54, 15, 25, NULL, NULL, NULL, true, '{}', '2025-09-19 01:03:54.334073+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (55, 15, 27, NULL, NULL, NULL, true, '{}', '2025-09-19 01:03:54.334073+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (56, 15, 28, NULL, NULL, NULL, true, '{}', '2025-09-19 01:03:54.334073+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (57, 15, 29, NULL, NULL, NULL, true, '{}', '2025-09-19 01:03:54.334073+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (58, 16, 30, 6, NULL, NULL, true, '{}', '2025-09-19 01:03:54.334073+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (59, 16, 30, 8, NULL, NULL, true, '{}', '2025-09-19 01:03:54.334073+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (40, 27, 35, NULL, 17, NULL, true, '{"color_program": "Limited Edition"}', '2025-09-19 00:54:53.652404+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (60, 37, 50, 5, 24, NULL, true, '{}', '2025-09-19 03:29:02.268695+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (61, 37, 50, 5, NULL, NULL, true, '{}', '2025-09-19 03:31:07.892102+00');
INSERT INTO "public"."variant" ("id", "style_id", "color_id", "fit_id", "fabric_id", "size_scale", "is_active", "attrs", "created_at") VALUES (62, 39, 52, 5, NULL, NULL, true, '{"brand_color_code": null}', '2025-09-19 04:45:37.930385+00');


--
-- TOC entry 4380 (class 0 OID 17479)
-- Dependencies: 379
-- Data for Name: variant_code; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (10, 20, 'AP6-308', 'product_code', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (11, 21, 'CP682', 'item_code', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (12, 22, 'CP684', 'item_code', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (13, 23, 'CP683', 'item_code', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (14, 24, 'BX291', 'item_code', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (15, 25, 'CA351', 'item_code', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (16, 26, 'CA352', 'item_code', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (17, 27, 'I0171104_G0F', 'suffix', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (18, 28, 'I0171104_G0F', 'suffix', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (19, 39, '109178-1275', 'derived_color_id', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (20, 40, '109178-14396', 'derived_color_id', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (21, 41, '109178-32383', 'derived_color_id', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (23, 43, '121483-14396', 'derived_color_id', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (24, 44, '123919-1274', 'derived_color_id', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (25, 45, '123919-33952', 'derived_color_id', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (26, 46, '118760-33952', 'derived_color_id', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (27, 47, '118308-1274', 'derived_color_id', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (28, 51, 'E71-002', 'product_code', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (29, 52, 'E70-998', 'product_code', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (30, 53, 'AB2-005', 'product_code', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (31, 54, 'F18-169', 'product_code', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (32, 55, 'AW1-262', 'product_code', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (33, 56, 'F18-163', 'product_code', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (34, 57, 'F18-205', 'product_code', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (35, 58, 'F78-985', 'product_code', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (36, 59, 'F77-495', 'product_code', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (22, 42, '121483-1274', 'derived_color_id', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (42, 60, 'ME053', 'item_code', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (43, 61, 'CC100', 'color_product_code', 'ALL');
INSERT INTO "public"."variant_code" ("id", "variant_id", "code", "code_type", "region") VALUES (44, 62, 'BX291', 'item_code', 'ALL');


--
-- TOC entry 4352 (class 0 OID 17025)
-- Dependencies: 347
-- Data for Name: schema_migrations; Type: TABLE DATA; Schema: realtime; Owner: -
--

INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20211116024918, '2025-09-19 00:26:53');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20211116045059, '2025-09-19 00:26:55');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20211116050929, '2025-09-19 00:26:58');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20211116051442, '2025-09-19 00:27:00');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20211116212300, '2025-09-19 00:27:02');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20211116213355, '2025-09-19 00:27:04');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20211116213934, '2025-09-19 00:27:06');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20211116214523, '2025-09-19 00:27:09');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20211122062447, '2025-09-19 00:27:11');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20211124070109, '2025-09-19 00:27:13');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20211202204204, '2025-09-19 00:27:15');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20211202204605, '2025-09-19 00:27:17');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20211210212804, '2025-09-19 00:27:24');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20211228014915, '2025-09-19 00:27:26');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20220107221237, '2025-09-19 00:27:28');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20220228202821, '2025-09-19 00:27:30');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20220312004840, '2025-09-19 00:27:32');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20220603231003, '2025-09-19 00:27:35');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20220603232444, '2025-09-19 00:27:37');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20220615214548, '2025-09-19 00:27:40');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20220712093339, '2025-09-19 00:27:42');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20220908172859, '2025-09-19 00:27:44');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20220916233421, '2025-09-19 00:27:46');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20230119133233, '2025-09-19 00:27:48');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20230128025114, '2025-09-19 00:27:51');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20230128025212, '2025-09-19 00:27:53');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20230227211149, '2025-09-19 00:27:55');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20230228184745, '2025-09-19 00:27:57');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20230308225145, '2025-09-19 00:27:59');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20230328144023, '2025-09-19 00:28:01');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20231018144023, '2025-09-19 00:28:03');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20231204144023, '2025-09-19 00:28:07');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20231204144024, '2025-09-19 00:28:09');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20231204144025, '2025-09-19 00:28:11');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20240108234812, '2025-09-19 00:28:13');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20240109165339, '2025-09-19 00:28:15');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20240227174441, '2025-09-19 00:28:18');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20240311171622, '2025-09-19 00:28:21');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20240321100241, '2025-09-19 00:28:26');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20240401105812, '2025-09-19 00:28:31');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20240418121054, '2025-09-19 00:28:34');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20240523004032, '2025-09-19 00:28:41');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20240618124746, '2025-09-19 00:28:43');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20240801235015, '2025-09-19 00:28:45');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20240805133720, '2025-09-19 00:28:48');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20240827160934, '2025-09-19 00:28:50');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20240919163303, '2025-09-19 00:28:52');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20240919163305, '2025-09-19 00:28:54');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20241019105805, '2025-09-19 00:28:56');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20241030150047, '2025-09-19 00:29:04');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20241108114728, '2025-09-19 00:29:07');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20241121104152, '2025-09-19 00:29:09');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20241130184212, '2025-09-19 00:29:11');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20241220035512, '2025-09-19 00:29:13');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20241220123912, '2025-09-19 00:29:15');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20241224161212, '2025-09-19 00:29:17');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20250107150512, '2025-09-19 00:29:19');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20250110162412, '2025-09-19 00:29:22');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20250123174212, '2025-09-19 00:29:24');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20250128220012, '2025-09-19 00:29:26');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20250506224012, '2025-09-19 00:29:27');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20250523164012, '2025-09-19 00:29:29');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20250714121412, '2025-09-19 00:29:31');
INSERT INTO "realtime"."schema_migrations" ("version", "inserted_at") VALUES (20250905041441, '2025-09-23 22:12:38');


--
-- TOC entry 4356 (class 0 OID 17131)
-- Dependencies: 352
-- Data for Name: subscription; Type: TABLE DATA; Schema: realtime; Owner: -
--



--
-- TOC entry 4337 (class 0 OID 16546)
-- Dependencies: 329
-- Data for Name: buckets; Type: TABLE DATA; Schema: storage; Owner: -
--



--
-- TOC entry 4403 (class 0 OID 43342)
-- Dependencies: 413
-- Data for Name: buckets_analytics; Type: TABLE DATA; Schema: storage; Owner: -
--



--
-- TOC entry 4339 (class 0 OID 16588)
-- Dependencies: 331
-- Data for Name: migrations; Type: TABLE DATA; Schema: storage; Owner: -
--

INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (0, 'create-migrations-table', 'e18db593bcde2aca2a408c4d1100f6abba2195df', '2025-09-19 00:26:50.303256');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (1, 'initialmigration', '6ab16121fbaa08bbd11b712d05f358f9b555d777', '2025-09-19 00:26:50.308594');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (2, 'storage-schema', '5c7968fd083fcea04050c1b7f6253c9771b99011', '2025-09-19 00:26:50.312991');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (3, 'pathtoken-column', '2cb1b0004b817b29d5b0a971af16bafeede4b70d', '2025-09-19 00:26:50.336383');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (4, 'add-migrations-rls', '427c5b63fe1c5937495d9c635c263ee7a5905058', '2025-09-19 00:26:50.389525');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (5, 'add-size-functions', '79e081a1455b63666c1294a440f8ad4b1e6a7f84', '2025-09-19 00:26:50.392509');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (6, 'change-column-name-in-get-size', 'f93f62afdf6613ee5e7e815b30d02dc990201044', '2025-09-19 00:26:50.395912');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (7, 'add-rls-to-buckets', 'e7e7f86adbc51049f341dfe8d30256c1abca17aa', '2025-09-19 00:26:50.39914');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (8, 'add-public-to-buckets', 'fd670db39ed65f9d08b01db09d6202503ca2bab3', '2025-09-19 00:26:50.401997');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (9, 'fix-search-function', '3a0af29f42e35a4d101c259ed955b67e1bee6825', '2025-09-19 00:26:50.4051');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (10, 'search-files-search-function', '68dc14822daad0ffac3746a502234f486182ef6e', '2025-09-19 00:26:50.408427');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (11, 'add-trigger-to-auto-update-updated_at-column', '7425bdb14366d1739fa8a18c83100636d74dcaa2', '2025-09-19 00:26:50.411818');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (12, 'add-automatic-avif-detection-flag', '8e92e1266eb29518b6a4c5313ab8f29dd0d08df9', '2025-09-19 00:26:50.418746');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (13, 'add-bucket-custom-limits', 'cce962054138135cd9a8c4bcd531598684b25e7d', '2025-09-19 00:26:50.421768');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (14, 'use-bytes-for-max-size', '941c41b346f9802b411f06f30e972ad4744dad27', '2025-09-19 00:26:50.424923');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (15, 'add-can-insert-object-function', '934146bc38ead475f4ef4b555c524ee5d66799e5', '2025-09-19 00:26:50.447235');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (16, 'add-version', '76debf38d3fd07dcfc747ca49096457d95b1221b', '2025-09-19 00:26:50.45096');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (17, 'drop-owner-foreign-key', 'f1cbb288f1b7a4c1eb8c38504b80ae2a0153d101', '2025-09-19 00:26:50.453591');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (18, 'add_owner_id_column_deprecate_owner', 'e7a511b379110b08e2f214be852c35414749fe66', '2025-09-19 00:26:50.456775');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (19, 'alter-default-value-objects-id', '02e5e22a78626187e00d173dc45f58fa66a4f043', '2025-09-19 00:26:50.461491');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (20, 'list-objects-with-delimiter', 'cd694ae708e51ba82bf012bba00caf4f3b6393b7', '2025-09-19 00:26:50.464413');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (21, 's3-multipart-uploads', '8c804d4a566c40cd1e4cc5b3725a664a9303657f', '2025-09-19 00:26:50.469472');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (22, 's3-multipart-uploads-big-ints', '9737dc258d2397953c9953d9b86920b8be0cdb73', '2025-09-19 00:26:50.485579');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (23, 'optimize-search-function', '9d7e604cddc4b56a5422dc68c9313f4a1b6f132c', '2025-09-19 00:26:50.494703');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (24, 'operation-function', '8312e37c2bf9e76bbe841aa5fda889206d2bf8aa', '2025-09-19 00:26:50.497293');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (25, 'custom-metadata', 'd974c6057c3db1c1f847afa0e291e6165693b990', '2025-09-19 00:26:50.500943');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (26, 'objects-prefixes', 'ef3f7871121cdc47a65308e6702519e853422ae2', '2025-10-10 23:16:37.421095');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (27, 'search-v2', '33b8f2a7ae53105f028e13e9fcda9dc4f356b4a2', '2025-10-10 23:16:37.504303');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (28, 'object-bucket-name-sorting', 'ba85ec41b62c6a30a3f136788227ee47f311c436', '2025-10-10 23:16:37.514266');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (29, 'create-prefixes', 'a7b1a22c0dc3ab630e3055bfec7ce7d2045c5b7b', '2025-10-10 23:16:37.52287');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (30, 'update-object-levels', '6c6f6cc9430d570f26284a24cf7b210599032db7', '2025-10-10 23:16:37.53097');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (31, 'objects-level-index', '33f1fef7ec7fea08bb892222f4f0f5d79bab5eb8', '2025-10-10 23:16:37.537677');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (32, 'backward-compatible-index-on-objects', '2d51eeb437a96868b36fcdfb1ddefdf13bef1647', '2025-10-10 23:16:37.546357');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (33, 'backward-compatible-index-on-prefixes', 'fe473390e1b8c407434c0e470655945b110507bf', '2025-10-10 23:16:37.552672');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (34, 'optimize-search-function-v1', '82b0e469a00e8ebce495e29bfa70a0797f7ebd2c', '2025-10-10 23:16:37.554276');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (35, 'add-insert-trigger-prefixes', '63bb9fd05deb3dc5e9fa66c83e82b152f0caf589', '2025-10-10 23:16:37.560751');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (36, 'optimise-existing-functions', '81cf92eb0c36612865a18016a38496c530443899', '2025-10-10 23:16:37.563958');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (37, 'add-bucket-name-length-trigger', '3944135b4e3e8b22d6d4cbb568fe3b0b51df15c1', '2025-10-10 23:16:37.575811');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (38, 'iceberg-catalog-flag-on-buckets', '19a8bd89d5dfa69af7f222a46c726b7c41e462c5', '2025-10-10 23:16:37.579401');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (39, 'add-search-v2-sort-support', '39cf7d1e6bf515f4b02e41237aba845a7b492853', '2025-10-10 23:16:37.60068');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (40, 'fix-prefix-race-conditions-optimized', 'fd02297e1c67df25a9fc110bf8c8a9af7fb06d1f', '2025-10-10 23:16:37.604249');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (41, 'add-object-level-update-trigger', '44c22478bf01744b2129efc480cd2edc9a7d60e9', '2025-10-10 23:16:37.611859');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (42, 'rollback-prefix-triggers', 'f2ab4f526ab7f979541082992593938c05ee4b47', '2025-10-10 23:16:37.615844');
INSERT INTO "storage"."migrations" ("id", "name", "hash", "executed_at") VALUES (43, 'fix-object-level', 'ab837ad8f1c7d00cc0b7310e989a23388ff29fc6', '2025-10-10 23:16:37.6203');


--
-- TOC entry 4338 (class 0 OID 16561)
-- Dependencies: 330
-- Data for Name: objects; Type: TABLE DATA; Schema: storage; Owner: -
--



--
-- TOC entry 4402 (class 0 OID 43298)
-- Dependencies: 412
-- Data for Name: prefixes; Type: TABLE DATA; Schema: storage; Owner: -
--



--
-- TOC entry 4353 (class 0 OID 17062)
-- Dependencies: 348
-- Data for Name: s3_multipart_uploads; Type: TABLE DATA; Schema: storage; Owner: -
--



--
-- TOC entry 4354 (class 0 OID 17076)
-- Dependencies: 349
-- Data for Name: s3_multipart_uploads_parts; Type: TABLE DATA; Schema: storage; Owner: -
--



--
-- TOC entry 4401 (class 0 OID 23422)
-- Dependencies: 411
-- Data for Name: hooks; Type: TABLE DATA; Schema: supabase_functions; Owner: -
--



--
-- TOC entry 4399 (class 0 OID 23413)
-- Dependencies: 409
-- Data for Name: migrations; Type: TABLE DATA; Schema: supabase_functions; Owner: -
--

INSERT INTO "supabase_functions"."migrations" ("version", "inserted_at") VALUES ('initial', '2025-09-24 06:19:18.272366+00');
INSERT INTO "supabase_functions"."migrations" ("version", "inserted_at") VALUES ('20210809183423_update_grants', '2025-09-24 06:19:18.272366+00');


--
-- TOC entry 3788 (class 0 OID 16658)
-- Dependencies: 332
-- Data for Name: secrets; Type: TABLE DATA; Schema: vault; Owner: -
--



--
-- TOC entry 4468 (class 0 OID 0)
-- Dependencies: 324
-- Name: refresh_tokens_id_seq; Type: SEQUENCE SET; Schema: auth; Owner: -
--

SELECT pg_catalog.setval('"auth"."refresh_tokens_id_seq"', 1, false);


--
-- TOC entry 4469 (class 0 OID 0)
-- Dependencies: 356
-- Name: __migrations_applied_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."__migrations_applied_id_seq"', 16, true);


--
-- TOC entry 4470 (class 0 OID 0)
-- Dependencies: 362
-- Name: brand_category_map_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."brand_category_map_id_seq"', 1, false);


--
-- TOC entry 4471 (class 0 OID 0)
-- Dependencies: 370
-- Name: brand_color_map_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."brand_color_map_id_seq"', 58, true);


--
-- TOC entry 4472 (class 0 OID 0)
-- Dependencies: 358
-- Name: brand_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."brand_id_seq"', 18, true);


--
-- TOC entry 4473 (class 0 OID 0)
-- Dependencies: 400
-- Name: brand_profile_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."brand_profile_id_seq"', 1, true);


--
-- TOC entry 4474 (class 0 OID 0)
-- Dependencies: 360
-- Name: category_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."category_id_seq"', 16, true);


--
-- TOC entry 4475 (class 0 OID 0)
-- Dependencies: 368
-- Name: color_catalog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."color_catalog_id_seq"', 52, true);


--
-- TOC entry 4476 (class 0 OID 0)
-- Dependencies: 390
-- Name: evidence_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."evidence_id_seq"', 1, false);


--
-- TOC entry 4477 (class 0 OID 0)
-- Dependencies: 364
-- Name: fabric_catalog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."fabric_catalog_id_seq"', 24, true);


--
-- TOC entry 4478 (class 0 OID 0)
-- Dependencies: 366
-- Name: fit_catalog_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."fit_catalog_id_seq"', 12, true);


--
-- TOC entry 4479 (class 0 OID 0)
-- Dependencies: 388
-- Name: ingest_run_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."ingest_run_id_seq"', 1, false);


--
-- TOC entry 4480 (class 0 OID 0)
-- Dependencies: 402
-- Name: ingestion_job_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."ingestion_job_id_seq"', 1, false);


--
-- TOC entry 4481 (class 0 OID 0)
-- Dependencies: 384
-- Name: inventory_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."inventory_history_id_seq"', 1, false);


--
-- TOC entry 4482 (class 0 OID 0)
-- Dependencies: 386
-- Name: media_asset_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."media_asset_id_seq"', 1, false);


--
-- TOC entry 4483 (class 0 OID 0)
-- Dependencies: 382
-- Name: price_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."price_history_id_seq"', 20, true);


--
-- TOC entry 4484 (class 0 OID 0)
-- Dependencies: 395
-- Name: product_image_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."product_image_id_seq"', 1, true);


--
-- TOC entry 4485 (class 0 OID 0)
-- Dependencies: 380
-- Name: product_url_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."product_url_id_seq"', 35, true);


--
-- TOC entry 4486 (class 0 OID 0)
-- Dependencies: 374
-- Name: style_code_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."style_code_id_seq"', 39, true);


--
-- TOC entry 4487 (class 0 OID 0)
-- Dependencies: 372
-- Name: style_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."style_id_seq"', 39, true);


--
-- TOC entry 4488 (class 0 OID 0)
-- Dependencies: 378
-- Name: variant_code_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."variant_code_id_seq"', 44, true);


--
-- TOC entry 4489 (class 0 OID 0)
-- Dependencies: 376
-- Name: variant_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."variant_id_seq"', 62, true);


--
-- TOC entry 4490 (class 0 OID 0)
-- Dependencies: 351
-- Name: subscription_id_seq; Type: SEQUENCE SET; Schema: realtime; Owner: -
--

SELECT pg_catalog.setval('"realtime"."subscription_id_seq"', 1, false);


--
-- TOC entry 4491 (class 0 OID 0)
-- Dependencies: 410
-- Name: hooks_id_seq; Type: SEQUENCE SET; Schema: supabase_functions; Owner: -
--

SELECT pg_catalog.setval('"supabase_functions"."hooks_id_seq"', 1, false);


--
-- TOC entry 3966 (class 2606 OID 16827)
-- Name: mfa_amr_claims amr_id_pk; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."mfa_amr_claims"
    ADD CONSTRAINT "amr_id_pk" PRIMARY KEY ("id");


--
-- TOC entry 3921 (class 2606 OID 16531)
-- Name: audit_log_entries audit_log_entries_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."audit_log_entries"
    ADD CONSTRAINT "audit_log_entries_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3989 (class 2606 OID 16933)
-- Name: flow_state flow_state_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."flow_state"
    ADD CONSTRAINT "flow_state_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3945 (class 2606 OID 16951)
-- Name: identities identities_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."identities"
    ADD CONSTRAINT "identities_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3947 (class 2606 OID 16961)
-- Name: identities identities_provider_id_provider_unique; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."identities"
    ADD CONSTRAINT "identities_provider_id_provider_unique" UNIQUE ("provider_id", "provider");


--
-- TOC entry 3919 (class 2606 OID 16524)
-- Name: instances instances_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."instances"
    ADD CONSTRAINT "instances_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3968 (class 2606 OID 16820)
-- Name: mfa_amr_claims mfa_amr_claims_session_id_authentication_method_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."mfa_amr_claims"
    ADD CONSTRAINT "mfa_amr_claims_session_id_authentication_method_pkey" UNIQUE ("session_id", "authentication_method");


--
-- TOC entry 3964 (class 2606 OID 16808)
-- Name: mfa_challenges mfa_challenges_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."mfa_challenges"
    ADD CONSTRAINT "mfa_challenges_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3956 (class 2606 OID 17001)
-- Name: mfa_factors mfa_factors_last_challenged_at_key; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."mfa_factors"
    ADD CONSTRAINT "mfa_factors_last_challenged_at_key" UNIQUE ("last_challenged_at");


--
-- TOC entry 3958 (class 2606 OID 16795)
-- Name: mfa_factors mfa_factors_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."mfa_factors"
    ADD CONSTRAINT "mfa_factors_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3999 (class 2606 OID 17022)
-- Name: oauth_clients oauth_clients_client_id_key; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."oauth_clients"
    ADD CONSTRAINT "oauth_clients_client_id_key" UNIQUE ("client_id");


--
-- TOC entry 4002 (class 2606 OID 17020)
-- Name: oauth_clients oauth_clients_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."oauth_clients"
    ADD CONSTRAINT "oauth_clients_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3993 (class 2606 OID 16986)
-- Name: one_time_tokens one_time_tokens_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."one_time_tokens"
    ADD CONSTRAINT "one_time_tokens_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3913 (class 2606 OID 16514)
-- Name: refresh_tokens refresh_tokens_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."refresh_tokens"
    ADD CONSTRAINT "refresh_tokens_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3916 (class 2606 OID 16738)
-- Name: refresh_tokens refresh_tokens_token_unique; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."refresh_tokens"
    ADD CONSTRAINT "refresh_tokens_token_unique" UNIQUE ("token");


--
-- TOC entry 3978 (class 2606 OID 16867)
-- Name: saml_providers saml_providers_entity_id_key; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."saml_providers"
    ADD CONSTRAINT "saml_providers_entity_id_key" UNIQUE ("entity_id");


--
-- TOC entry 3980 (class 2606 OID 16865)
-- Name: saml_providers saml_providers_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."saml_providers"
    ADD CONSTRAINT "saml_providers_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3985 (class 2606 OID 16881)
-- Name: saml_relay_states saml_relay_states_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."saml_relay_states"
    ADD CONSTRAINT "saml_relay_states_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3924 (class 2606 OID 16537)
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."schema_migrations"
    ADD CONSTRAINT "schema_migrations_pkey" PRIMARY KEY ("version");


--
-- TOC entry 3951 (class 2606 OID 16759)
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."sessions"
    ADD CONSTRAINT "sessions_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3975 (class 2606 OID 16848)
-- Name: sso_domains sso_domains_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."sso_domains"
    ADD CONSTRAINT "sso_domains_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3970 (class 2606 OID 16839)
-- Name: sso_providers sso_providers_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."sso_providers"
    ADD CONSTRAINT "sso_providers_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3906 (class 2606 OID 16921)
-- Name: users users_phone_key; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."users"
    ADD CONSTRAINT "users_phone_key" UNIQUE ("phone");


--
-- TOC entry 3908 (class 2606 OID 16501)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."users"
    ADD CONSTRAINT "users_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4018 (class 2606 OID 17307)
-- Name: __migrations_applied __migrations_applied_filename_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."__migrations_applied"
    ADD CONSTRAINT "__migrations_applied_filename_key" UNIQUE ("filename");


--
-- TOC entry 4020 (class 2606 OID 17305)
-- Name: __migrations_applied __migrations_applied_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."__migrations_applied"
    ADD CONSTRAINT "__migrations_applied_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4030 (class 2606 OID 17344)
-- Name: brand_category_map brand_category_map_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."brand_category_map"
    ADD CONSTRAINT "brand_category_map_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4044 (class 2606 OID 17396)
-- Name: brand_color_map brand_color_map_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."brand_color_map"
    ADD CONSTRAINT "brand_color_map_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4022 (class 2606 OID 17318)
-- Name: brand brand_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."brand"
    ADD CONSTRAINT "brand_name_key" UNIQUE ("name");


--
-- TOC entry 4024 (class 2606 OID 17316)
-- Name: brand brand_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."brand"
    ADD CONSTRAINT "brand_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4087 (class 2606 OID 18881)
-- Name: brand_profile brand_profile_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."brand_profile"
    ADD CONSTRAINT "brand_profile_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4089 (class 2606 OID 18883)
-- Name: brand_profile brand_profile_slug_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."brand_profile"
    ADD CONSTRAINT "brand_profile_slug_key" UNIQUE ("slug");


--
-- TOC entry 4026 (class 2606 OID 17327)
-- Name: category category_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."category"
    ADD CONSTRAINT "category_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4028 (class 2606 OID 17329)
-- Name: category category_slug_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."category"
    ADD CONSTRAINT "category_slug_key" UNIQUE ("slug");


--
-- TOC entry 4040 (class 2606 OID 17387)
-- Name: color_catalog color_catalog_canonical_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."color_catalog"
    ADD CONSTRAINT "color_catalog_canonical_key" UNIQUE ("canonical");


--
-- TOC entry 4042 (class 2606 OID 17385)
-- Name: color_catalog color_catalog_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."color_catalog"
    ADD CONSTRAINT "color_catalog_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4081 (class 2606 OID 17589)
-- Name: evidence evidence_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."evidence"
    ADD CONSTRAINT "evidence_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4032 (class 2606 OID 17365)
-- Name: fabric_catalog fabric_catalog_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."fabric_catalog"
    ADD CONSTRAINT "fabric_catalog_name_key" UNIQUE ("name");


--
-- TOC entry 4034 (class 2606 OID 17363)
-- Name: fabric_catalog fabric_catalog_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."fabric_catalog"
    ADD CONSTRAINT "fabric_catalog_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4036 (class 2606 OID 17376)
-- Name: fit_catalog fit_catalog_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."fit_catalog"
    ADD CONSTRAINT "fit_catalog_name_key" UNIQUE ("name");


--
-- TOC entry 4038 (class 2606 OID 17374)
-- Name: fit_catalog fit_catalog_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."fit_catalog"
    ADD CONSTRAINT "fit_catalog_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4079 (class 2606 OID 17574)
-- Name: ingest_run ingest_run_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."ingest_run"
    ADD CONSTRAINT "ingest_run_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4092 (class 2606 OID 18898)
-- Name: ingestion_job ingestion_job_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."ingestion_job"
    ADD CONSTRAINT "ingestion_job_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4075 (class 2606 OID 17540)
-- Name: inventory_history inventory_history_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."inventory_history"
    ADD CONSTRAINT "inventory_history_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4077 (class 2606 OID 17554)
-- Name: media_asset media_asset_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."media_asset"
    ADD CONSTRAINT "media_asset_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4070 (class 2606 OID 17524)
-- Name: price_history price_history_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."price_history"
    ADD CONSTRAINT "price_history_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4072 (class 2606 OID 17526)
-- Name: price_history price_history_variant_id_region_captured_at_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."price_history"
    ADD CONSTRAINT "price_history_variant_id_region_captured_at_key" UNIQUE ("variant_id", "region", "captured_at");


--
-- TOC entry 4083 (class 2606 OID 18597)
-- Name: product_image product_image_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."product_image"
    ADD CONSTRAINT "product_image_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4085 (class 2606 OID 18599)
-- Name: product_image product_image_style_id_variant_id_url_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."product_image"
    ADD CONSTRAINT "product_image_style_id_variant_id_url_key" UNIQUE ("style_id", "variant_id", "url");


--
-- TOC entry 4067 (class 2606 OID 17505)
-- Name: product_url product_url_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."product_url"
    ADD CONSTRAINT "product_url_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4050 (class 2606 OID 17418)
-- Name: style style_brand_id_name_category_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."style"
    ADD CONSTRAINT "style_brand_id_name_category_id_key" UNIQUE ("brand_id", "name", "category_id");


--
-- TOC entry 4054 (class 2606 OID 17438)
-- Name: style_code style_code_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."style_code"
    ADD CONSTRAINT "style_code_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4056 (class 2606 OID 17440)
-- Name: style_code style_code_style_id_code_region_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."style_code"
    ADD CONSTRAINT "style_code_style_id_code_region_key" UNIQUE ("style_id", "code", "region");


--
-- TOC entry 4052 (class 2606 OID 17416)
-- Name: style style_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."style"
    ADD CONSTRAINT "style_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4047 (class 2606 OID 18183)
-- Name: brand_color_map uq_brand_color_map_brand_original; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."brand_color_map"
    ADD CONSTRAINT "uq_brand_color_map_brand_original" UNIQUE ("brand_id", "original");


--
-- TOC entry 4062 (class 2606 OID 17487)
-- Name: variant_code variant_code_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."variant_code"
    ADD CONSTRAINT "variant_code_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4064 (class 2606 OID 17489)
-- Name: variant_code variant_code_variant_id_code_region_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."variant_code"
    ADD CONSTRAINT "variant_code_variant_id_code_region_key" UNIQUE ("variant_id", "code", "region");


--
-- TOC entry 4060 (class 2606 OID 17457)
-- Name: variant variant_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."variant"
    ADD CONSTRAINT "variant_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4016 (class 2606 OID 17291)
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: realtime; Owner: -
--

ALTER TABLE ONLY "realtime"."messages"
    ADD CONSTRAINT "messages_pkey" PRIMARY KEY ("id", "inserted_at");


--
-- TOC entry 4012 (class 2606 OID 17139)
-- Name: subscription pk_subscription; Type: CONSTRAINT; Schema: realtime; Owner: -
--

ALTER TABLE ONLY "realtime"."subscription"
    ADD CONSTRAINT "pk_subscription" PRIMARY KEY ("id");


--
-- TOC entry 4004 (class 2606 OID 17029)
-- Name: schema_migrations schema_migrations_pkey; Type: CONSTRAINT; Schema: realtime; Owner: -
--

ALTER TABLE ONLY "realtime"."schema_migrations"
    ADD CONSTRAINT "schema_migrations_pkey" PRIMARY KEY ("version");


--
-- TOC entry 4103 (class 2606 OID 43352)
-- Name: buckets_analytics buckets_analytics_pkey; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY "storage"."buckets_analytics"
    ADD CONSTRAINT "buckets_analytics_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3927 (class 2606 OID 16554)
-- Name: buckets buckets_pkey; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY "storage"."buckets"
    ADD CONSTRAINT "buckets_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3937 (class 2606 OID 16595)
-- Name: migrations migrations_name_key; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY "storage"."migrations"
    ADD CONSTRAINT "migrations_name_key" UNIQUE ("name");


--
-- TOC entry 3939 (class 2606 OID 16593)
-- Name: migrations migrations_pkey; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY "storage"."migrations"
    ADD CONSTRAINT "migrations_pkey" PRIMARY KEY ("id");


--
-- TOC entry 3935 (class 2606 OID 16571)
-- Name: objects objects_pkey; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY "storage"."objects"
    ADD CONSTRAINT "objects_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4101 (class 2606 OID 43307)
-- Name: prefixes prefixes_pkey; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY "storage"."prefixes"
    ADD CONSTRAINT "prefixes_pkey" PRIMARY KEY ("bucket_id", "level", "name");


--
-- TOC entry 4009 (class 2606 OID 17085)
-- Name: s3_multipart_uploads_parts s3_multipart_uploads_parts_pkey; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY "storage"."s3_multipart_uploads_parts"
    ADD CONSTRAINT "s3_multipart_uploads_parts_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4007 (class 2606 OID 17070)
-- Name: s3_multipart_uploads s3_multipart_uploads_pkey; Type: CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY "storage"."s3_multipart_uploads"
    ADD CONSTRAINT "s3_multipart_uploads_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4096 (class 2606 OID 23430)
-- Name: hooks hooks_pkey; Type: CONSTRAINT; Schema: supabase_functions; Owner: -
--

ALTER TABLE ONLY "supabase_functions"."hooks"
    ADD CONSTRAINT "hooks_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4094 (class 2606 OID 23420)
-- Name: migrations migrations_pkey; Type: CONSTRAINT; Schema: supabase_functions; Owner: -
--

ALTER TABLE ONLY "supabase_functions"."migrations"
    ADD CONSTRAINT "migrations_pkey" PRIMARY KEY ("version");


--
-- TOC entry 3922 (class 1259 OID 16532)
-- Name: audit_logs_instance_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "audit_logs_instance_id_idx" ON "auth"."audit_log_entries" USING "btree" ("instance_id");


--
-- TOC entry 3896 (class 1259 OID 16748)
-- Name: confirmation_token_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX "confirmation_token_idx" ON "auth"."users" USING "btree" ("confirmation_token") WHERE (("confirmation_token")::"text" !~ '^[0-9 ]*$'::"text");


--
-- TOC entry 3897 (class 1259 OID 16750)
-- Name: email_change_token_current_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX "email_change_token_current_idx" ON "auth"."users" USING "btree" ("email_change_token_current") WHERE (("email_change_token_current")::"text" !~ '^[0-9 ]*$'::"text");


--
-- TOC entry 3898 (class 1259 OID 16751)
-- Name: email_change_token_new_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX "email_change_token_new_idx" ON "auth"."users" USING "btree" ("email_change_token_new") WHERE (("email_change_token_new")::"text" !~ '^[0-9 ]*$'::"text");


--
-- TOC entry 3954 (class 1259 OID 16829)
-- Name: factor_id_created_at_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "factor_id_created_at_idx" ON "auth"."mfa_factors" USING "btree" ("user_id", "created_at");


--
-- TOC entry 3987 (class 1259 OID 16937)
-- Name: flow_state_created_at_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "flow_state_created_at_idx" ON "auth"."flow_state" USING "btree" ("created_at" DESC);


--
-- TOC entry 3943 (class 1259 OID 16917)
-- Name: identities_email_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "identities_email_idx" ON "auth"."identities" USING "btree" ("email" "text_pattern_ops");


--
-- TOC entry 4492 (class 0 OID 0)
-- Dependencies: 3943
-- Name: INDEX "identities_email_idx"; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON INDEX "auth"."identities_email_idx" IS 'Auth: Ensures indexed queries on the email column';


--
-- TOC entry 3948 (class 1259 OID 16745)
-- Name: identities_user_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "identities_user_id_idx" ON "auth"."identities" USING "btree" ("user_id");


--
-- TOC entry 3990 (class 1259 OID 16934)
-- Name: idx_auth_code; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "idx_auth_code" ON "auth"."flow_state" USING "btree" ("auth_code");


--
-- TOC entry 3991 (class 1259 OID 16935)
-- Name: idx_user_id_auth_method; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "idx_user_id_auth_method" ON "auth"."flow_state" USING "btree" ("user_id", "authentication_method");


--
-- TOC entry 3962 (class 1259 OID 16940)
-- Name: mfa_challenge_created_at_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "mfa_challenge_created_at_idx" ON "auth"."mfa_challenges" USING "btree" ("created_at" DESC);


--
-- TOC entry 3959 (class 1259 OID 16801)
-- Name: mfa_factors_user_friendly_name_unique; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX "mfa_factors_user_friendly_name_unique" ON "auth"."mfa_factors" USING "btree" ("friendly_name", "user_id") WHERE (TRIM(BOTH FROM "friendly_name") <> ''::"text");


--
-- TOC entry 3960 (class 1259 OID 16946)
-- Name: mfa_factors_user_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "mfa_factors_user_id_idx" ON "auth"."mfa_factors" USING "btree" ("user_id");


--
-- TOC entry 3997 (class 1259 OID 17023)
-- Name: oauth_clients_client_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "oauth_clients_client_id_idx" ON "auth"."oauth_clients" USING "btree" ("client_id");


--
-- TOC entry 4000 (class 1259 OID 17024)
-- Name: oauth_clients_deleted_at_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "oauth_clients_deleted_at_idx" ON "auth"."oauth_clients" USING "btree" ("deleted_at");


--
-- TOC entry 3994 (class 1259 OID 16993)
-- Name: one_time_tokens_relates_to_hash_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "one_time_tokens_relates_to_hash_idx" ON "auth"."one_time_tokens" USING "hash" ("relates_to");


--
-- TOC entry 3995 (class 1259 OID 16992)
-- Name: one_time_tokens_token_hash_hash_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "one_time_tokens_token_hash_hash_idx" ON "auth"."one_time_tokens" USING "hash" ("token_hash");


--
-- TOC entry 3996 (class 1259 OID 16994)
-- Name: one_time_tokens_user_id_token_type_key; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX "one_time_tokens_user_id_token_type_key" ON "auth"."one_time_tokens" USING "btree" ("user_id", "token_type");


--
-- TOC entry 3899 (class 1259 OID 16752)
-- Name: reauthentication_token_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX "reauthentication_token_idx" ON "auth"."users" USING "btree" ("reauthentication_token") WHERE (("reauthentication_token")::"text" !~ '^[0-9 ]*$'::"text");


--
-- TOC entry 3900 (class 1259 OID 16749)
-- Name: recovery_token_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX "recovery_token_idx" ON "auth"."users" USING "btree" ("recovery_token") WHERE (("recovery_token")::"text" !~ '^[0-9 ]*$'::"text");


--
-- TOC entry 3909 (class 1259 OID 16515)
-- Name: refresh_tokens_instance_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "refresh_tokens_instance_id_idx" ON "auth"."refresh_tokens" USING "btree" ("instance_id");


--
-- TOC entry 3910 (class 1259 OID 16516)
-- Name: refresh_tokens_instance_id_user_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "refresh_tokens_instance_id_user_id_idx" ON "auth"."refresh_tokens" USING "btree" ("instance_id", "user_id");


--
-- TOC entry 3911 (class 1259 OID 16744)
-- Name: refresh_tokens_parent_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "refresh_tokens_parent_idx" ON "auth"."refresh_tokens" USING "btree" ("parent");


--
-- TOC entry 3914 (class 1259 OID 16831)
-- Name: refresh_tokens_session_id_revoked_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "refresh_tokens_session_id_revoked_idx" ON "auth"."refresh_tokens" USING "btree" ("session_id", "revoked");


--
-- TOC entry 3917 (class 1259 OID 16936)
-- Name: refresh_tokens_updated_at_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "refresh_tokens_updated_at_idx" ON "auth"."refresh_tokens" USING "btree" ("updated_at" DESC);


--
-- TOC entry 3981 (class 1259 OID 16873)
-- Name: saml_providers_sso_provider_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "saml_providers_sso_provider_id_idx" ON "auth"."saml_providers" USING "btree" ("sso_provider_id");


--
-- TOC entry 3982 (class 1259 OID 16938)
-- Name: saml_relay_states_created_at_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "saml_relay_states_created_at_idx" ON "auth"."saml_relay_states" USING "btree" ("created_at" DESC);


--
-- TOC entry 3983 (class 1259 OID 16888)
-- Name: saml_relay_states_for_email_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "saml_relay_states_for_email_idx" ON "auth"."saml_relay_states" USING "btree" ("for_email");


--
-- TOC entry 3986 (class 1259 OID 16887)
-- Name: saml_relay_states_sso_provider_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "saml_relay_states_sso_provider_id_idx" ON "auth"."saml_relay_states" USING "btree" ("sso_provider_id");


--
-- TOC entry 3949 (class 1259 OID 16939)
-- Name: sessions_not_after_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "sessions_not_after_idx" ON "auth"."sessions" USING "btree" ("not_after" DESC);


--
-- TOC entry 3952 (class 1259 OID 16830)
-- Name: sessions_user_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "sessions_user_id_idx" ON "auth"."sessions" USING "btree" ("user_id");


--
-- TOC entry 3973 (class 1259 OID 16855)
-- Name: sso_domains_domain_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX "sso_domains_domain_idx" ON "auth"."sso_domains" USING "btree" ("lower"("domain"));


--
-- TOC entry 3976 (class 1259 OID 16854)
-- Name: sso_domains_sso_provider_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "sso_domains_sso_provider_id_idx" ON "auth"."sso_domains" USING "btree" ("sso_provider_id");


--
-- TOC entry 3971 (class 1259 OID 16840)
-- Name: sso_providers_resource_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX "sso_providers_resource_id_idx" ON "auth"."sso_providers" USING "btree" ("lower"("resource_id"));


--
-- TOC entry 3972 (class 1259 OID 17002)
-- Name: sso_providers_resource_id_pattern_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "sso_providers_resource_id_pattern_idx" ON "auth"."sso_providers" USING "btree" ("resource_id" "text_pattern_ops");


--
-- TOC entry 3961 (class 1259 OID 16999)
-- Name: unique_phone_factor_per_user; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX "unique_phone_factor_per_user" ON "auth"."mfa_factors" USING "btree" ("user_id", "phone");


--
-- TOC entry 3953 (class 1259 OID 16828)
-- Name: user_id_created_at_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "user_id_created_at_idx" ON "auth"."sessions" USING "btree" ("user_id", "created_at");


--
-- TOC entry 3901 (class 1259 OID 16908)
-- Name: users_email_partial_key; Type: INDEX; Schema: auth; Owner: -
--

CREATE UNIQUE INDEX "users_email_partial_key" ON "auth"."users" USING "btree" ("email") WHERE ("is_sso_user" = false);


--
-- TOC entry 4493 (class 0 OID 0)
-- Dependencies: 3901
-- Name: INDEX "users_email_partial_key"; Type: COMMENT; Schema: auth; Owner: -
--

COMMENT ON INDEX "auth"."users_email_partial_key" IS 'Auth: A partial unique index that applies only when is_sso_user is false';


--
-- TOC entry 3902 (class 1259 OID 16746)
-- Name: users_instance_id_email_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "users_instance_id_email_idx" ON "auth"."users" USING "btree" ("instance_id", "lower"(("email")::"text"));


--
-- TOC entry 3903 (class 1259 OID 16505)
-- Name: users_instance_id_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "users_instance_id_idx" ON "auth"."users" USING "btree" ("instance_id");


--
-- TOC entry 3904 (class 1259 OID 16963)
-- Name: users_is_anonymous_idx; Type: INDEX; Schema: auth; Owner: -
--

CREATE INDEX "users_is_anonymous_idx" ON "auth"."users" USING "btree" ("is_anonymous");


--
-- TOC entry 4045 (class 1259 OID 18184)
-- Name: idx_brand_color_map_brand_original; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "idx_brand_color_map_brand_original" ON "public"."brand_color_map" USING "btree" ("brand_id", "original");


--
-- TOC entry 4073 (class 1259 OID 17599)
-- Name: idx_inventory_variant_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "idx_inventory_variant_time" ON "public"."inventory_history" USING "btree" ("variant_id", "captured_at" DESC);


--
-- TOC entry 4090 (class 1259 OID 18899)
-- Name: idx_job_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "idx_job_status" ON "public"."ingestion_job" USING "btree" ("status");


--
-- TOC entry 4068 (class 1259 OID 17598)
-- Name: idx_price_variant_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "idx_price_variant_time" ON "public"."price_history" USING "btree" ("variant_id", "captured_at" DESC);


--
-- TOC entry 4048 (class 1259 OID 17595)
-- Name: idx_style_brand_cat; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "idx_style_brand_cat" ON "public"."style" USING "btree" ("brand_id", "category_id");


--
-- TOC entry 4065 (class 1259 OID 17600)
-- Name: idx_url_style_current; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "idx_url_style_current" ON "public"."product_url" USING "btree" ("style_id", "is_current") WHERE ("is_current" = true);


--
-- TOC entry 4057 (class 1259 OID 17597)
-- Name: idx_variant_core; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "idx_variant_core" ON "public"."variant" USING "btree" ("color_id", "fit_id", "fabric_id");


--
-- TOC entry 4058 (class 1259 OID 17596)
-- Name: idx_variant_style; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "idx_variant_style" ON "public"."variant" USING "btree" ("style_id");


--
-- TOC entry 4010 (class 1259 OID 17292)
-- Name: ix_realtime_subscription_entity; Type: INDEX; Schema: realtime; Owner: -
--

CREATE INDEX "ix_realtime_subscription_entity" ON "realtime"."subscription" USING "btree" ("entity");


--
-- TOC entry 4014 (class 1259 OID 23360)
-- Name: messages_inserted_at_topic_index; Type: INDEX; Schema: realtime; Owner: -
--

CREATE INDEX "messages_inserted_at_topic_index" ON ONLY "realtime"."messages" USING "btree" ("inserted_at" DESC, "topic") WHERE (("extension" = 'broadcast'::"text") AND ("private" IS TRUE));


--
-- TOC entry 4013 (class 1259 OID 17192)
-- Name: subscription_subscription_id_entity_filters_key; Type: INDEX; Schema: realtime; Owner: -
--

CREATE UNIQUE INDEX "subscription_subscription_id_entity_filters_key" ON "realtime"."subscription" USING "btree" ("subscription_id", "entity", "filters");


--
-- TOC entry 3925 (class 1259 OID 16560)
-- Name: bname; Type: INDEX; Schema: storage; Owner: -
--

CREATE UNIQUE INDEX "bname" ON "storage"."buckets" USING "btree" ("name");


--
-- TOC entry 3928 (class 1259 OID 16582)
-- Name: bucketid_objname; Type: INDEX; Schema: storage; Owner: -
--

CREATE UNIQUE INDEX "bucketid_objname" ON "storage"."objects" USING "btree" ("bucket_id", "name");


--
-- TOC entry 4005 (class 1259 OID 17096)
-- Name: idx_multipart_uploads_list; Type: INDEX; Schema: storage; Owner: -
--

CREATE INDEX "idx_multipart_uploads_list" ON "storage"."s3_multipart_uploads" USING "btree" ("bucket_id", "key", "created_at");


--
-- TOC entry 3929 (class 1259 OID 43325)
-- Name: idx_name_bucket_level_unique; Type: INDEX; Schema: storage; Owner: -
--

CREATE UNIQUE INDEX "idx_name_bucket_level_unique" ON "storage"."objects" USING "btree" ("name" COLLATE "C", "bucket_id", "level");


--
-- TOC entry 3930 (class 1259 OID 17061)
-- Name: idx_objects_bucket_id_name; Type: INDEX; Schema: storage; Owner: -
--

CREATE INDEX "idx_objects_bucket_id_name" ON "storage"."objects" USING "btree" ("bucket_id", "name" COLLATE "C");


--
-- TOC entry 3931 (class 1259 OID 43327)
-- Name: idx_objects_lower_name; Type: INDEX; Schema: storage; Owner: -
--

CREATE INDEX "idx_objects_lower_name" ON "storage"."objects" USING "btree" (("path_tokens"["level"]), "lower"("name") "text_pattern_ops", "bucket_id", "level");


--
-- TOC entry 4099 (class 1259 OID 43328)
-- Name: idx_prefixes_lower_name; Type: INDEX; Schema: storage; Owner: -
--

CREATE INDEX "idx_prefixes_lower_name" ON "storage"."prefixes" USING "btree" ("bucket_id", "level", (("string_to_array"("name", '/'::"text"))["level"]), "lower"("name") "text_pattern_ops");


--
-- TOC entry 3932 (class 1259 OID 16583)
-- Name: name_prefix_search; Type: INDEX; Schema: storage; Owner: -
--

CREATE INDEX "name_prefix_search" ON "storage"."objects" USING "btree" ("name" "text_pattern_ops");


--
-- TOC entry 3933 (class 1259 OID 43326)
-- Name: objects_bucket_id_level_idx; Type: INDEX; Schema: storage; Owner: -
--

CREATE UNIQUE INDEX "objects_bucket_id_level_idx" ON "storage"."objects" USING "btree" ("bucket_id", "level", "name" COLLATE "C");


--
-- TOC entry 4097 (class 1259 OID 23432)
-- Name: supabase_functions_hooks_h_table_id_h_name_idx; Type: INDEX; Schema: supabase_functions; Owner: -
--

CREATE INDEX "supabase_functions_hooks_h_table_id_h_name_idx" ON "supabase_functions"."hooks" USING "btree" ("hook_table_id", "hook_name");


--
-- TOC entry 4098 (class 1259 OID 23431)
-- Name: supabase_functions_hooks_request_id_idx; Type: INDEX; Schema: supabase_functions; Owner: -
--

CREATE INDEX "supabase_functions_hooks_request_id_idx" ON "supabase_functions"."hooks" USING "btree" ("request_id");


--
-- TOC entry 4149 (class 2620 OID 17144)
-- Name: subscription tr_check_filters; Type: TRIGGER; Schema: realtime; Owner: -
--

CREATE TRIGGER "tr_check_filters" BEFORE INSERT OR UPDATE ON "realtime"."subscription" FOR EACH ROW EXECUTE FUNCTION "realtime"."subscription_check_filters"();


--
-- TOC entry 4144 (class 2620 OID 43335)
-- Name: buckets enforce_bucket_name_length_trigger; Type: TRIGGER; Schema: storage; Owner: -
--

CREATE TRIGGER "enforce_bucket_name_length_trigger" BEFORE INSERT OR UPDATE OF "name" ON "storage"."buckets" FOR EACH ROW EXECUTE FUNCTION "storage"."enforce_bucket_name_length"();


--
-- TOC entry 4145 (class 2620 OID 43365)
-- Name: objects objects_delete_delete_prefix; Type: TRIGGER; Schema: storage; Owner: -
--

CREATE TRIGGER "objects_delete_delete_prefix" AFTER DELETE ON "storage"."objects" FOR EACH ROW EXECUTE FUNCTION "storage"."delete_prefix_hierarchy_trigger"();


--
-- TOC entry 4146 (class 2620 OID 43321)
-- Name: objects objects_insert_create_prefix; Type: TRIGGER; Schema: storage; Owner: -
--

CREATE TRIGGER "objects_insert_create_prefix" BEFORE INSERT ON "storage"."objects" FOR EACH ROW EXECUTE FUNCTION "storage"."objects_insert_prefix_trigger"();


--
-- TOC entry 4147 (class 2620 OID 43364)
-- Name: objects objects_update_create_prefix; Type: TRIGGER; Schema: storage; Owner: -
--

CREATE TRIGGER "objects_update_create_prefix" BEFORE UPDATE ON "storage"."objects" FOR EACH ROW WHEN ((("new"."name" <> "old"."name") OR ("new"."bucket_id" <> "old"."bucket_id"))) EXECUTE FUNCTION "storage"."objects_update_prefix_trigger"();


--
-- TOC entry 4150 (class 2620 OID 43331)
-- Name: prefixes prefixes_create_hierarchy; Type: TRIGGER; Schema: storage; Owner: -
--

CREATE TRIGGER "prefixes_create_hierarchy" BEFORE INSERT ON "storage"."prefixes" FOR EACH ROW WHEN (("pg_trigger_depth"() < 1)) EXECUTE FUNCTION "storage"."prefixes_insert_trigger"();


--
-- TOC entry 4151 (class 2620 OID 43366)
-- Name: prefixes prefixes_delete_hierarchy; Type: TRIGGER; Schema: storage; Owner: -
--

CREATE TRIGGER "prefixes_delete_hierarchy" AFTER DELETE ON "storage"."prefixes" FOR EACH ROW EXECUTE FUNCTION "storage"."delete_prefix_hierarchy_trigger"();


--
-- TOC entry 4148 (class 2620 OID 17049)
-- Name: objects update_objects_updated_at; Type: TRIGGER; Schema: storage; Owner: -
--

CREATE TRIGGER "update_objects_updated_at" BEFORE UPDATE ON "storage"."objects" FOR EACH ROW EXECUTE FUNCTION "storage"."update_updated_at_column"();


--
-- TOC entry 4106 (class 2606 OID 16732)
-- Name: identities identities_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."identities"
    ADD CONSTRAINT "identities_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;


--
-- TOC entry 4110 (class 2606 OID 16821)
-- Name: mfa_amr_claims mfa_amr_claims_session_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."mfa_amr_claims"
    ADD CONSTRAINT "mfa_amr_claims_session_id_fkey" FOREIGN KEY ("session_id") REFERENCES "auth"."sessions"("id") ON DELETE CASCADE;


--
-- TOC entry 4109 (class 2606 OID 16809)
-- Name: mfa_challenges mfa_challenges_auth_factor_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."mfa_challenges"
    ADD CONSTRAINT "mfa_challenges_auth_factor_id_fkey" FOREIGN KEY ("factor_id") REFERENCES "auth"."mfa_factors"("id") ON DELETE CASCADE;


--
-- TOC entry 4108 (class 2606 OID 16796)
-- Name: mfa_factors mfa_factors_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."mfa_factors"
    ADD CONSTRAINT "mfa_factors_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;


--
-- TOC entry 4115 (class 2606 OID 16987)
-- Name: one_time_tokens one_time_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."one_time_tokens"
    ADD CONSTRAINT "one_time_tokens_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;


--
-- TOC entry 4104 (class 2606 OID 16765)
-- Name: refresh_tokens refresh_tokens_session_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."refresh_tokens"
    ADD CONSTRAINT "refresh_tokens_session_id_fkey" FOREIGN KEY ("session_id") REFERENCES "auth"."sessions"("id") ON DELETE CASCADE;


--
-- TOC entry 4112 (class 2606 OID 16868)
-- Name: saml_providers saml_providers_sso_provider_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."saml_providers"
    ADD CONSTRAINT "saml_providers_sso_provider_id_fkey" FOREIGN KEY ("sso_provider_id") REFERENCES "auth"."sso_providers"("id") ON DELETE CASCADE;


--
-- TOC entry 4113 (class 2606 OID 16941)
-- Name: saml_relay_states saml_relay_states_flow_state_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."saml_relay_states"
    ADD CONSTRAINT "saml_relay_states_flow_state_id_fkey" FOREIGN KEY ("flow_state_id") REFERENCES "auth"."flow_state"("id") ON DELETE CASCADE;


--
-- TOC entry 4114 (class 2606 OID 16882)
-- Name: saml_relay_states saml_relay_states_sso_provider_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."saml_relay_states"
    ADD CONSTRAINT "saml_relay_states_sso_provider_id_fkey" FOREIGN KEY ("sso_provider_id") REFERENCES "auth"."sso_providers"("id") ON DELETE CASCADE;


--
-- TOC entry 4107 (class 2606 OID 16760)
-- Name: sessions sessions_user_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."sessions"
    ADD CONSTRAINT "sessions_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id") ON DELETE CASCADE;


--
-- TOC entry 4111 (class 2606 OID 16849)
-- Name: sso_domains sso_domains_sso_provider_id_fkey; Type: FK CONSTRAINT; Schema: auth; Owner: -
--

ALTER TABLE ONLY "auth"."sso_domains"
    ADD CONSTRAINT "sso_domains_sso_provider_id_fkey" FOREIGN KEY ("sso_provider_id") REFERENCES "auth"."sso_providers"("id") ON DELETE CASCADE;


--
-- TOC entry 4120 (class 2606 OID 17345)
-- Name: brand_category_map brand_category_map_brand_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."brand_category_map"
    ADD CONSTRAINT "brand_category_map_brand_id_fkey" FOREIGN KEY ("brand_id") REFERENCES "public"."brand"("id");


--
-- TOC entry 4121 (class 2606 OID 17350)
-- Name: brand_category_map brand_category_map_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."brand_category_map"
    ADD CONSTRAINT "brand_category_map_category_id_fkey" FOREIGN KEY ("category_id") REFERENCES "public"."category"("id");


--
-- TOC entry 4122 (class 2606 OID 17397)
-- Name: brand_color_map brand_color_map_brand_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."brand_color_map"
    ADD CONSTRAINT "brand_color_map_brand_id_fkey" FOREIGN KEY ("brand_id") REFERENCES "public"."brand"("id");


--
-- TOC entry 4123 (class 2606 OID 17402)
-- Name: brand_color_map brand_color_map_color_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."brand_color_map"
    ADD CONSTRAINT "brand_color_map_color_id_fkey" FOREIGN KEY ("color_id") REFERENCES "public"."color_catalog"("id");


--
-- TOC entry 4142 (class 2606 OID 18884)
-- Name: brand_profile brand_profile_brand_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."brand_profile"
    ADD CONSTRAINT "brand_profile_brand_id_fkey" FOREIGN KEY ("brand_id") REFERENCES "public"."brand"("id") ON DELETE CASCADE;


--
-- TOC entry 4119 (class 2606 OID 17330)
-- Name: category category_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."category"
    ADD CONSTRAINT "category_parent_id_fkey" FOREIGN KEY ("parent_id") REFERENCES "public"."category"("id");


--
-- TOC entry 4139 (class 2606 OID 17590)
-- Name: evidence evidence_ingest_run_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."evidence"
    ADD CONSTRAINT "evidence_ingest_run_id_fkey" FOREIGN KEY ("ingest_run_id") REFERENCES "public"."ingest_run"("id");


--
-- TOC entry 4138 (class 2606 OID 17575)
-- Name: ingest_run ingest_run_brand_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."ingest_run"
    ADD CONSTRAINT "ingest_run_brand_id_fkey" FOREIGN KEY ("brand_id") REFERENCES "public"."brand"("id");


--
-- TOC entry 4135 (class 2606 OID 17541)
-- Name: inventory_history inventory_history_variant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."inventory_history"
    ADD CONSTRAINT "inventory_history_variant_id_fkey" FOREIGN KEY ("variant_id") REFERENCES "public"."variant"("id");


--
-- TOC entry 4136 (class 2606 OID 17555)
-- Name: media_asset media_asset_style_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."media_asset"
    ADD CONSTRAINT "media_asset_style_id_fkey" FOREIGN KEY ("style_id") REFERENCES "public"."style"("id");


--
-- TOC entry 4137 (class 2606 OID 17560)
-- Name: media_asset media_asset_variant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."media_asset"
    ADD CONSTRAINT "media_asset_variant_id_fkey" FOREIGN KEY ("variant_id") REFERENCES "public"."variant"("id");


--
-- TOC entry 4134 (class 2606 OID 17527)
-- Name: price_history price_history_variant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."price_history"
    ADD CONSTRAINT "price_history_variant_id_fkey" FOREIGN KEY ("variant_id") REFERENCES "public"."variant"("id");


--
-- TOC entry 4140 (class 2606 OID 18600)
-- Name: product_image product_image_style_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."product_image"
    ADD CONSTRAINT "product_image_style_id_fkey" FOREIGN KEY ("style_id") REFERENCES "public"."style"("id") ON DELETE CASCADE;


--
-- TOC entry 4141 (class 2606 OID 18605)
-- Name: product_image product_image_variant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."product_image"
    ADD CONSTRAINT "product_image_variant_id_fkey" FOREIGN KEY ("variant_id") REFERENCES "public"."variant"("id") ON DELETE CASCADE;


--
-- TOC entry 4132 (class 2606 OID 17506)
-- Name: product_url product_url_style_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."product_url"
    ADD CONSTRAINT "product_url_style_id_fkey" FOREIGN KEY ("style_id") REFERENCES "public"."style"("id");


--
-- TOC entry 4133 (class 2606 OID 17511)
-- Name: product_url product_url_variant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."product_url"
    ADD CONSTRAINT "product_url_variant_id_fkey" FOREIGN KEY ("variant_id") REFERENCES "public"."variant"("id");


--
-- TOC entry 4124 (class 2606 OID 17419)
-- Name: style style_brand_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."style"
    ADD CONSTRAINT "style_brand_id_fkey" FOREIGN KEY ("brand_id") REFERENCES "public"."brand"("id");


--
-- TOC entry 4125 (class 2606 OID 17424)
-- Name: style style_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."style"
    ADD CONSTRAINT "style_category_id_fkey" FOREIGN KEY ("category_id") REFERENCES "public"."category"("id");


--
-- TOC entry 4126 (class 2606 OID 17441)
-- Name: style_code style_code_style_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."style_code"
    ADD CONSTRAINT "style_code_style_id_fkey" FOREIGN KEY ("style_id") REFERENCES "public"."style"("id");


--
-- TOC entry 4131 (class 2606 OID 17490)
-- Name: variant_code variant_code_variant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."variant_code"
    ADD CONSTRAINT "variant_code_variant_id_fkey" FOREIGN KEY ("variant_id") REFERENCES "public"."variant"("id");


--
-- TOC entry 4127 (class 2606 OID 17463)
-- Name: variant variant_color_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."variant"
    ADD CONSTRAINT "variant_color_id_fkey" FOREIGN KEY ("color_id") REFERENCES "public"."color_catalog"("id");


--
-- TOC entry 4128 (class 2606 OID 17473)
-- Name: variant variant_fabric_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."variant"
    ADD CONSTRAINT "variant_fabric_id_fkey" FOREIGN KEY ("fabric_id") REFERENCES "public"."fabric_catalog"("id");


--
-- TOC entry 4129 (class 2606 OID 17468)
-- Name: variant variant_fit_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."variant"
    ADD CONSTRAINT "variant_fit_id_fkey" FOREIGN KEY ("fit_id") REFERENCES "public"."fit_catalog"("id");


--
-- TOC entry 4130 (class 2606 OID 17458)
-- Name: variant variant_style_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."variant"
    ADD CONSTRAINT "variant_style_id_fkey" FOREIGN KEY ("style_id") REFERENCES "public"."style"("id");


--
-- TOC entry 4105 (class 2606 OID 16572)
-- Name: objects objects_bucketId_fkey; Type: FK CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY "storage"."objects"
    ADD CONSTRAINT "objects_bucketId_fkey" FOREIGN KEY ("bucket_id") REFERENCES "storage"."buckets"("id");


--
-- TOC entry 4143 (class 2606 OID 43308)
-- Name: prefixes prefixes_bucketId_fkey; Type: FK CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY "storage"."prefixes"
    ADD CONSTRAINT "prefixes_bucketId_fkey" FOREIGN KEY ("bucket_id") REFERENCES "storage"."buckets"("id");


--
-- TOC entry 4116 (class 2606 OID 17071)
-- Name: s3_multipart_uploads s3_multipart_uploads_bucket_id_fkey; Type: FK CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY "storage"."s3_multipart_uploads"
    ADD CONSTRAINT "s3_multipart_uploads_bucket_id_fkey" FOREIGN KEY ("bucket_id") REFERENCES "storage"."buckets"("id");


--
-- TOC entry 4117 (class 2606 OID 17091)
-- Name: s3_multipart_uploads_parts s3_multipart_uploads_parts_bucket_id_fkey; Type: FK CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY "storage"."s3_multipart_uploads_parts"
    ADD CONSTRAINT "s3_multipart_uploads_parts_bucket_id_fkey" FOREIGN KEY ("bucket_id") REFERENCES "storage"."buckets"("id");


--
-- TOC entry 4118 (class 2606 OID 17086)
-- Name: s3_multipart_uploads_parts s3_multipart_uploads_parts_upload_id_fkey; Type: FK CONSTRAINT; Schema: storage; Owner: -
--

ALTER TABLE ONLY "storage"."s3_multipart_uploads_parts"
    ADD CONSTRAINT "s3_multipart_uploads_parts_upload_id_fkey" FOREIGN KEY ("upload_id") REFERENCES "storage"."s3_multipart_uploads"("id") ON DELETE CASCADE;


--
-- TOC entry 4309 (class 0 OID 16525)
-- Dependencies: 327
-- Name: audit_log_entries; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE "auth"."audit_log_entries" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4323 (class 0 OID 16927)
-- Dependencies: 344
-- Name: flow_state; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE "auth"."flow_state" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4314 (class 0 OID 16725)
-- Dependencies: 335
-- Name: identities; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE "auth"."identities" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4308 (class 0 OID 16518)
-- Dependencies: 326
-- Name: instances; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE "auth"."instances" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4318 (class 0 OID 16814)
-- Dependencies: 339
-- Name: mfa_amr_claims; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE "auth"."mfa_amr_claims" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4317 (class 0 OID 16802)
-- Dependencies: 338
-- Name: mfa_challenges; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE "auth"."mfa_challenges" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4316 (class 0 OID 16789)
-- Dependencies: 337
-- Name: mfa_factors; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE "auth"."mfa_factors" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4324 (class 0 OID 16977)
-- Dependencies: 345
-- Name: one_time_tokens; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE "auth"."one_time_tokens" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4307 (class 0 OID 16507)
-- Dependencies: 325
-- Name: refresh_tokens; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE "auth"."refresh_tokens" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4321 (class 0 OID 16856)
-- Dependencies: 342
-- Name: saml_providers; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE "auth"."saml_providers" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4322 (class 0 OID 16874)
-- Dependencies: 343
-- Name: saml_relay_states; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE "auth"."saml_relay_states" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4310 (class 0 OID 16533)
-- Dependencies: 328
-- Name: schema_migrations; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE "auth"."schema_migrations" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4315 (class 0 OID 16755)
-- Dependencies: 336
-- Name: sessions; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE "auth"."sessions" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4320 (class 0 OID 16841)
-- Dependencies: 341
-- Name: sso_domains; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE "auth"."sso_domains" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4319 (class 0 OID 16832)
-- Dependencies: 340
-- Name: sso_providers; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE "auth"."sso_providers" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4306 (class 0 OID 16495)
-- Dependencies: 323
-- Name: users; Type: ROW SECURITY; Schema: auth; Owner: -
--

ALTER TABLE "auth"."users" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4327 (class 0 OID 17277)
-- Dependencies: 355
-- Name: messages; Type: ROW SECURITY; Schema: realtime; Owner: -
--

ALTER TABLE "realtime"."messages" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4311 (class 0 OID 16546)
-- Dependencies: 329
-- Name: buckets; Type: ROW SECURITY; Schema: storage; Owner: -
--

ALTER TABLE "storage"."buckets" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4329 (class 0 OID 43342)
-- Dependencies: 413
-- Name: buckets_analytics; Type: ROW SECURITY; Schema: storage; Owner: -
--

ALTER TABLE "storage"."buckets_analytics" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4313 (class 0 OID 16588)
-- Dependencies: 331
-- Name: migrations; Type: ROW SECURITY; Schema: storage; Owner: -
--

ALTER TABLE "storage"."migrations" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4312 (class 0 OID 16561)
-- Dependencies: 330
-- Name: objects; Type: ROW SECURITY; Schema: storage; Owner: -
--

ALTER TABLE "storage"."objects" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4328 (class 0 OID 43298)
-- Dependencies: 412
-- Name: prefixes; Type: ROW SECURITY; Schema: storage; Owner: -
--

ALTER TABLE "storage"."prefixes" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4325 (class 0 OID 17062)
-- Dependencies: 348
-- Name: s3_multipart_uploads; Type: ROW SECURITY; Schema: storage; Owner: -
--

ALTER TABLE "storage"."s3_multipart_uploads" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4326 (class 0 OID 17076)
-- Dependencies: 349
-- Name: s3_multipart_uploads_parts; Type: ROW SECURITY; Schema: storage; Owner: -
--

ALTER TABLE "storage"."s3_multipart_uploads_parts" ENABLE ROW LEVEL SECURITY;

--
-- TOC entry 4330 (class 6104 OID 16426)
-- Name: supabase_realtime; Type: PUBLICATION; Schema: -; Owner: -
--

CREATE PUBLICATION "supabase_realtime" WITH (publish = 'insert, update, delete, truncate');


--
-- TOC entry 3781 (class 3466 OID 16621)
-- Name: issue_graphql_placeholder; Type: EVENT TRIGGER; Schema: -; Owner: -
--

CREATE EVENT TRIGGER "issue_graphql_placeholder" ON "sql_drop"
         WHEN TAG IN ('DROP EXTENSION')
   EXECUTE FUNCTION "extensions"."set_graphql_placeholder"();


--
-- TOC entry 3786 (class 3466 OID 16700)
-- Name: issue_pg_cron_access; Type: EVENT TRIGGER; Schema: -; Owner: -
--

CREATE EVENT TRIGGER "issue_pg_cron_access" ON "ddl_command_end"
         WHEN TAG IN ('CREATE EXTENSION')
   EXECUTE FUNCTION "extensions"."grant_pg_cron_access"();


--
-- TOC entry 3780 (class 3466 OID 16619)
-- Name: issue_pg_graphql_access; Type: EVENT TRIGGER; Schema: -; Owner: -
--

CREATE EVENT TRIGGER "issue_pg_graphql_access" ON "ddl_command_end"
         WHEN TAG IN ('CREATE FUNCTION')
   EXECUTE FUNCTION "extensions"."grant_pg_graphql_access"();


--
-- TOC entry 3787 (class 3466 OID 16703)
-- Name: issue_pg_net_access; Type: EVENT TRIGGER; Schema: -; Owner: -
--

CREATE EVENT TRIGGER "issue_pg_net_access" ON "ddl_command_end"
         WHEN TAG IN ('CREATE EXTENSION')
   EXECUTE FUNCTION "extensions"."grant_pg_net_access"();


--
-- TOC entry 3782 (class 3466 OID 16622)
-- Name: pgrst_ddl_watch; Type: EVENT TRIGGER; Schema: -; Owner: -
--

CREATE EVENT TRIGGER "pgrst_ddl_watch" ON "ddl_command_end"
   EXECUTE FUNCTION "extensions"."pgrst_ddl_watch"();


--
-- TOC entry 3783 (class 3466 OID 16623)
-- Name: pgrst_drop_watch; Type: EVENT TRIGGER; Schema: -; Owner: -
--

CREATE EVENT TRIGGER "pgrst_drop_watch" ON "sql_drop"
   EXECUTE FUNCTION "extensions"."pgrst_drop_watch"();


-- Completed on 2025-10-10 19:38:13 EDT

--
-- PostgreSQL database dump complete
--

\unrestrict oqEaczop9hctEKCKmaJeIRhcIdTd1FdgE46ERXivFUbwFlXPqJpbJWvJctskrq7

