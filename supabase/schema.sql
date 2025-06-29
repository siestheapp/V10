

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;


CREATE SCHEMA IF NOT EXISTS "public";


ALTER SCHEMA "public" OWNER TO "pg_database_owner";


COMMENT ON SCHEMA "public" IS 'standard public schema';


SET default_tablespace = '';

SET default_table_access_method = "heap";


CREATE TABLE IF NOT EXISTS "public"."admins" (
    "id" integer NOT NULL,
    "email" "text" NOT NULL,
    "name" "text",
    "role" "text" DEFAULT 'contributor'::"text",
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "notes" "text",
    CONSTRAINT "admins_role_check" CHECK (("role" = ANY (ARRAY['admin'::"text", 'moderator'::"text", 'contributor'::"text"])))
);


ALTER TABLE "public"."admins" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."admins_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."admins_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."admins_id_seq" OWNED BY "public"."admins"."id";



CREATE TABLE IF NOT EXISTS "public"."body_measurements" (
    "id" integer NOT NULL,
    "user_id" integer,
    "chest" numeric,
    "waist" numeric,
    "neck" numeric,
    "sleeve" numeric,
    "hip" numeric,
    "inseam" numeric,
    "length" numeric,
    "unit" "text" DEFAULT 'in'::"text",
    "confidence_score" numeric,
    "notes" "text",
    "source" "text",
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp without time zone,
    CONSTRAINT "body_measurements_unit_check" CHECK (("unit" = ANY (ARRAY['in'::"text", 'cm'::"text"])))
);


ALTER TABLE "public"."body_measurements" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."body_measurements_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."body_measurements_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."body_measurements_id_seq" OWNED BY "public"."body_measurements"."id";



CREATE TABLE IF NOT EXISTS "public"."brands" (
    "id" integer NOT NULL,
    "name" "text" NOT NULL,
    "region" "text",
    "default_unit" "text" DEFAULT 'in'::"text",
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "created_by" integer,
    "updated_at" timestamp without time zone,
    "updated_by" integer,
    "notes" "text",
    CONSTRAINT "brands_default_unit_check" CHECK (("default_unit" = ANY (ARRAY['in'::"text", 'cm'::"text"])))
);


ALTER TABLE "public"."brands" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."brands_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."brands_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."brands_id_seq" OWNED BY "public"."brands"."id";



CREATE TABLE IF NOT EXISTS "public"."categories" (
    "id" integer NOT NULL,
    "name" "text" NOT NULL,
    "description" "text",
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "created_by" integer,
    "updated_at" timestamp without time zone,
    "updated_by" integer
);


ALTER TABLE "public"."categories" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."categories_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."categories_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."categories_id_seq" OWNED BY "public"."categories"."id";



CREATE TABLE IF NOT EXISTS "public"."feedback_codes" (
    "id" integer NOT NULL,
    "feedback_text" "text" NOT NULL,
    "feedback_type" "text" NOT NULL,
    "is_positive" boolean,
    CONSTRAINT "feedback_codes_feedback_type_check" CHECK (("feedback_type" = ANY (ARRAY['fit'::"text", 'length'::"text", 'other'::"text"])))
);


ALTER TABLE "public"."feedback_codes" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."feedback_codes_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."feedback_codes_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."feedback_codes_id_seq" OWNED BY "public"."feedback_codes"."id";



CREATE TABLE IF NOT EXISTS "public"."fit_zones" (
    "id" integer NOT NULL,
    "user_id" integer,
    "category_id" integer,
    "subcategory_id" integer,
    "dimension" "text" NOT NULL,
    "fit_type" "text" NOT NULL,
    "min_value" numeric,
    "max_value" numeric,
    "unit" "text" DEFAULT 'in'::"text",
    "range_text" "text",
    "notes" "text",
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp without time zone,
    CONSTRAINT "fit_zones_dimension_check" CHECK (("dimension" = ANY (ARRAY['chest'::"text", 'waist'::"text", 'neck'::"text", 'sleeve'::"text", 'hip'::"text", 'length'::"text"]))),
    CONSTRAINT "fit_zones_fit_type_check" CHECK (("fit_type" = ANY (ARRAY['tight'::"text", 'perfect'::"text", 'relaxed'::"text"]))),
    CONSTRAINT "fit_zones_unit_check" CHECK (("unit" = ANY (ARRAY['in'::"text", 'cm'::"text"])))
);


ALTER TABLE "public"."fit_zones" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."fit_zones_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."fit_zones_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."fit_zones_id_seq" OWNED BY "public"."fit_zones"."id";



CREATE TABLE IF NOT EXISTS "public"."raw_size_guides" (
    "id" integer NOT NULL,
    "brand_id" integer,
    "gender" "text",
    "category_id" integer,
    "subcategory_id" integer,
    "fit_type" "text" DEFAULT 'Regular'::"text",
    "source_url" "text",
    "screenshot_path" "text",
    "raw_text" "text",
    "raw_table_json" "jsonb",
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "uploaded_by" integer,
    CONSTRAINT "raw_size_guides_fit_type_check" CHECK (("fit_type" = ANY (ARRAY['Regular'::"text", 'Slim'::"text", 'Tall'::"text"]))),
    CONSTRAINT "raw_size_guides_gender_check" CHECK (("gender" = ANY (ARRAY['Male'::"text", 'Female'::"text", 'Unisex'::"text"])))
);


ALTER TABLE "public"."raw_size_guides" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."raw_size_guides_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."raw_size_guides_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."raw_size_guides_id_seq" OWNED BY "public"."raw_size_guides"."id";



CREATE TABLE IF NOT EXISTS "public"."size_guide_entries" (
    "id" integer NOT NULL,
    "size_guide_id" integer,
    "size_label" "text" NOT NULL,
    "chest_min" numeric,
    "chest_max" numeric,
    "chest_range" "text",
    "waist_min" numeric,
    "waist_max" numeric,
    "waist_range" "text",
    "sleeve_min" numeric,
    "sleeve_max" numeric,
    "sleeve_range" "text",
    "neck_min" numeric,
    "neck_max" numeric,
    "neck_range" "text",
    "center_back_length" numeric,
    "notes" "text",
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "created_by" integer,
    "updated_at" timestamp without time zone,
    "updated_by" integer
);


ALTER TABLE "public"."size_guide_entries" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."size_guide_entries_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."size_guide_entries_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."size_guide_entries_id_seq" OWNED BY "public"."size_guide_entries"."id";



CREATE TABLE IF NOT EXISTS "public"."size_guides" (
    "id" integer NOT NULL,
    "brand_id" integer,
    "gender" "text" NOT NULL,
    "category_id" integer,
    "subcategory_id" integer,
    "fit_type" "text" DEFAULT 'Regular'::"text",
    "guide_level" "text" DEFAULT 'brand_level'::"text",
    "version" integer DEFAULT 1,
    "source_url" "text",
    "size_guide_header" "text",
    "notes" "text",
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "created_by" integer,
    "updated_at" timestamp without time zone,
    "updated_by" integer,
    CONSTRAINT "size_guides_fit_type_check" CHECK (("fit_type" = ANY (ARRAY['Regular'::"text", 'Slim'::"text", 'Tall'::"text"]))),
    CONSTRAINT "size_guides_gender_check" CHECK (("gender" = ANY (ARRAY['Male'::"text", 'Female'::"text", 'Unisex'::"text"]))),
    CONSTRAINT "size_guides_guide_level_check" CHECK (("guide_level" = ANY (ARRAY['brand_level'::"text", 'category_level'::"text", 'product_level'::"text"])))
);


ALTER TABLE "public"."size_guides" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."size_guides_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."size_guides_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."size_guides_id_seq" OWNED BY "public"."size_guides"."id";



CREATE TABLE IF NOT EXISTS "public"."standardization_log" (
    "id" integer NOT NULL,
    "brand_id" integer,
    "original_term" "text" NOT NULL,
    "standardized_term" "text" NOT NULL,
    "source_table" "text",
    "notes" "text",
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "created_by" integer
);


ALTER TABLE "public"."standardization_log" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."standardization_log_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."standardization_log_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."standardization_log_id_seq" OWNED BY "public"."standardization_log"."id";



CREATE TABLE IF NOT EXISTS "public"."subcategories" (
    "id" integer NOT NULL,
    "category_id" integer,
    "name" "text" NOT NULL,
    "description" "text",
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "created_by" integer,
    "updated_at" timestamp without time zone,
    "updated_by" integer
);


ALTER TABLE "public"."subcategories" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."subcategories_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."subcategories_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."subcategories_id_seq" OWNED BY "public"."subcategories"."id";



CREATE TABLE IF NOT EXISTS "public"."user_garment_feedback" (
    "id" integer NOT NULL,
    "user_garment_id" integer,
    "dimension" "text" NOT NULL,
    "feedback_code_id" integer,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "created_by" integer,
    CONSTRAINT "user_garment_feedback_dimension_check" CHECK (("dimension" = ANY (ARRAY['overall'::"text", 'chest'::"text", 'waist'::"text", 'sleeve'::"text", 'neck'::"text", 'hip'::"text", 'length'::"text"])))
);


ALTER TABLE "public"."user_garment_feedback" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."user_garment_feedback_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."user_garment_feedback_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."user_garment_feedback_id_seq" OWNED BY "public"."user_garment_feedback"."id";



CREATE TABLE IF NOT EXISTS "public"."user_garments" (
    "id" integer NOT NULL,
    "user_id" integer,
    "brand_id" integer,
    "category_id" integer,
    "subcategory_id" integer,
    "gender" "text",
    "size_label" "text" NOT NULL,
    "fit_type" "text" DEFAULT 'Regular'::"text",
    "unit" "text" DEFAULT 'in'::"text",
    "product_name" "text",
    "product_url" "text",
    "product_code" "text",
    "tag_photo_path" "text",
    "owns_garment" boolean DEFAULT true,
    "size_guide_id" integer,
    "size_guide_entry_id" integer,
    "fit_feedback" "text",
    "feedback_timestamp" timestamp without time zone,
    "notes" "text",
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "created_by" integer,
    "updated_at" timestamp without time zone,
    "updated_by" integer,
    CONSTRAINT "user_garments_fit_type_check" CHECK (("fit_type" = ANY (ARRAY['Regular'::"text", 'Slim'::"text", 'Tall'::"text"]))),
    CONSTRAINT "user_garments_gender_check" CHECK (("gender" = ANY (ARRAY['Male'::"text", 'Female'::"text", 'Unisex'::"text"]))),
    CONSTRAINT "user_garments_unit_check" CHECK (("unit" = ANY (ARRAY['in'::"text", 'cm'::"text"])))
);


ALTER TABLE "public"."user_garments" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."user_garments_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."user_garments_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."user_garments_id_seq" OWNED BY "public"."user_garments"."id";



CREATE TABLE IF NOT EXISTS "public"."users" (
    "id" integer NOT NULL,
    "email" "text" NOT NULL,
    "created_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "gender" "text" NOT NULL,
    "height_in" numeric,
    "preferred_units" "text" DEFAULT 'in'::"text",
    "notes" "text",
    CONSTRAINT "users_gender_check" CHECK (("gender" = ANY (ARRAY['Male'::"text", 'Female'::"text", 'Unisex'::"text"]))),
    CONSTRAINT "users_preferred_units_check" CHECK (("preferred_units" = ANY (ARRAY['in'::"text", 'cm'::"text"])))
);


ALTER TABLE "public"."users" OWNER TO "postgres";


CREATE SEQUENCE IF NOT EXISTS "public"."users_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE "public"."users_id_seq" OWNER TO "postgres";


ALTER SEQUENCE "public"."users_id_seq" OWNED BY "public"."users"."id";



ALTER TABLE ONLY "public"."admins" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."admins_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."body_measurements" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."body_measurements_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."brands" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."brands_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."categories" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."categories_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."feedback_codes" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."feedback_codes_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."fit_zones" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."fit_zones_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."raw_size_guides" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."raw_size_guides_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."size_guide_entries" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."size_guide_entries_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."size_guides" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."size_guides_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."standardization_log" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."standardization_log_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."subcategories" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."subcategories_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."user_garment_feedback" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."user_garment_feedback_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."user_garments" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."user_garments_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."users" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."users_id_seq"'::"regclass");



ALTER TABLE ONLY "public"."admins"
    ADD CONSTRAINT "admins_email_key" UNIQUE ("email");



ALTER TABLE ONLY "public"."admins"
    ADD CONSTRAINT "admins_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."body_measurements"
    ADD CONSTRAINT "body_measurements_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."brands"
    ADD CONSTRAINT "brands_name_key" UNIQUE ("name");



ALTER TABLE ONLY "public"."brands"
    ADD CONSTRAINT "brands_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."categories"
    ADD CONSTRAINT "categories_name_key" UNIQUE ("name");



ALTER TABLE ONLY "public"."categories"
    ADD CONSTRAINT "categories_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."feedback_codes"
    ADD CONSTRAINT "feedback_codes_feedback_text_key" UNIQUE ("feedback_text");



ALTER TABLE ONLY "public"."feedback_codes"
    ADD CONSTRAINT "feedback_codes_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."fit_zones"
    ADD CONSTRAINT "fit_zones_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."raw_size_guides"
    ADD CONSTRAINT "raw_size_guides_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."size_guide_entries"
    ADD CONSTRAINT "size_guide_entries_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."size_guide_entries"
    ADD CONSTRAINT "size_guide_entries_size_guide_id_size_label_key" UNIQUE ("size_guide_id", "size_label");



ALTER TABLE ONLY "public"."size_guides"
    ADD CONSTRAINT "size_guides_brand_id_gender_category_id_fit_type_version_key" UNIQUE ("brand_id", "gender", "category_id", "fit_type", "version");



ALTER TABLE ONLY "public"."size_guides"
    ADD CONSTRAINT "size_guides_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."standardization_log"
    ADD CONSTRAINT "standardization_log_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."subcategories"
    ADD CONSTRAINT "subcategories_category_id_name_key" UNIQUE ("category_id", "name");



ALTER TABLE ONLY "public"."subcategories"
    ADD CONSTRAINT "subcategories_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."user_garment_feedback"
    ADD CONSTRAINT "user_garment_feedback_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."user_garments"
    ADD CONSTRAINT "user_garments_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."users"
    ADD CONSTRAINT "users_email_key" UNIQUE ("email");



ALTER TABLE ONLY "public"."users"
    ADD CONSTRAINT "users_pkey" PRIMARY KEY ("id");



ALTER TABLE ONLY "public"."body_measurements"
    ADD CONSTRAINT "body_measurements_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."brands"
    ADD CONSTRAINT "brands_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "public"."admins"("id");



ALTER TABLE ONLY "public"."brands"
    ADD CONSTRAINT "brands_updated_by_fkey" FOREIGN KEY ("updated_by") REFERENCES "public"."admins"("id");



ALTER TABLE ONLY "public"."categories"
    ADD CONSTRAINT "categories_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "public"."admins"("id");



ALTER TABLE ONLY "public"."categories"
    ADD CONSTRAINT "categories_updated_by_fkey" FOREIGN KEY ("updated_by") REFERENCES "public"."admins"("id");



ALTER TABLE ONLY "public"."fit_zones"
    ADD CONSTRAINT "fit_zones_category_id_fkey" FOREIGN KEY ("category_id") REFERENCES "public"."categories"("id");



ALTER TABLE ONLY "public"."fit_zones"
    ADD CONSTRAINT "fit_zones_subcategory_id_fkey" FOREIGN KEY ("subcategory_id") REFERENCES "public"."subcategories"("id");



ALTER TABLE ONLY "public"."fit_zones"
    ADD CONSTRAINT "fit_zones_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."raw_size_guides"
    ADD CONSTRAINT "raw_size_guides_brand_id_fkey" FOREIGN KEY ("brand_id") REFERENCES "public"."brands"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."raw_size_guides"
    ADD CONSTRAINT "raw_size_guides_category_id_fkey" FOREIGN KEY ("category_id") REFERENCES "public"."categories"("id");



ALTER TABLE ONLY "public"."raw_size_guides"
    ADD CONSTRAINT "raw_size_guides_subcategory_id_fkey" FOREIGN KEY ("subcategory_id") REFERENCES "public"."subcategories"("id");



ALTER TABLE ONLY "public"."raw_size_guides"
    ADD CONSTRAINT "raw_size_guides_uploaded_by_fkey" FOREIGN KEY ("uploaded_by") REFERENCES "public"."admins"("id");



ALTER TABLE ONLY "public"."size_guide_entries"
    ADD CONSTRAINT "size_guide_entries_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "public"."admins"("id");



ALTER TABLE ONLY "public"."size_guide_entries"
    ADD CONSTRAINT "size_guide_entries_size_guide_id_fkey" FOREIGN KEY ("size_guide_id") REFERENCES "public"."size_guides"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."size_guide_entries"
    ADD CONSTRAINT "size_guide_entries_updated_by_fkey" FOREIGN KEY ("updated_by") REFERENCES "public"."admins"("id");



ALTER TABLE ONLY "public"."size_guides"
    ADD CONSTRAINT "size_guides_brand_id_fkey" FOREIGN KEY ("brand_id") REFERENCES "public"."brands"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."size_guides"
    ADD CONSTRAINT "size_guides_category_id_fkey" FOREIGN KEY ("category_id") REFERENCES "public"."categories"("id");



ALTER TABLE ONLY "public"."size_guides"
    ADD CONSTRAINT "size_guides_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "public"."admins"("id");



ALTER TABLE ONLY "public"."size_guides"
    ADD CONSTRAINT "size_guides_subcategory_id_fkey" FOREIGN KEY ("subcategory_id") REFERENCES "public"."subcategories"("id");



ALTER TABLE ONLY "public"."size_guides"
    ADD CONSTRAINT "size_guides_updated_by_fkey" FOREIGN KEY ("updated_by") REFERENCES "public"."admins"("id");



ALTER TABLE ONLY "public"."standardization_log"
    ADD CONSTRAINT "standardization_log_brand_id_fkey" FOREIGN KEY ("brand_id") REFERENCES "public"."brands"("id");



ALTER TABLE ONLY "public"."standardization_log"
    ADD CONSTRAINT "standardization_log_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "public"."admins"("id");



ALTER TABLE ONLY "public"."subcategories"
    ADD CONSTRAINT "subcategories_category_id_fkey" FOREIGN KEY ("category_id") REFERENCES "public"."categories"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."subcategories"
    ADD CONSTRAINT "subcategories_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "public"."admins"("id");



ALTER TABLE ONLY "public"."subcategories"
    ADD CONSTRAINT "subcategories_updated_by_fkey" FOREIGN KEY ("updated_by") REFERENCES "public"."admins"("id");



ALTER TABLE ONLY "public"."user_garment_feedback"
    ADD CONSTRAINT "user_garment_feedback_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "public"."admins"("id");



ALTER TABLE ONLY "public"."user_garment_feedback"
    ADD CONSTRAINT "user_garment_feedback_feedback_code_id_fkey" FOREIGN KEY ("feedback_code_id") REFERENCES "public"."feedback_codes"("id");



ALTER TABLE ONLY "public"."user_garment_feedback"
    ADD CONSTRAINT "user_garment_feedback_user_garment_id_fkey" FOREIGN KEY ("user_garment_id") REFERENCES "public"."user_garments"("id") ON DELETE CASCADE;



ALTER TABLE ONLY "public"."user_garments"
    ADD CONSTRAINT "user_garments_brand_id_fkey" FOREIGN KEY ("brand_id") REFERENCES "public"."brands"("id");



ALTER TABLE ONLY "public"."user_garments"
    ADD CONSTRAINT "user_garments_category_id_fkey" FOREIGN KEY ("category_id") REFERENCES "public"."categories"("id");



ALTER TABLE ONLY "public"."user_garments"
    ADD CONSTRAINT "user_garments_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "public"."admins"("id");



ALTER TABLE ONLY "public"."user_garments"
    ADD CONSTRAINT "user_garments_size_guide_entry_id_fkey" FOREIGN KEY ("size_guide_entry_id") REFERENCES "public"."size_guide_entries"("id");



ALTER TABLE ONLY "public"."user_garments"
    ADD CONSTRAINT "user_garments_size_guide_id_fkey" FOREIGN KEY ("size_guide_id") REFERENCES "public"."size_guides"("id");



ALTER TABLE ONLY "public"."user_garments"
    ADD CONSTRAINT "user_garments_subcategory_id_fkey" FOREIGN KEY ("subcategory_id") REFERENCES "public"."subcategories"("id");



ALTER TABLE ONLY "public"."user_garments"
    ADD CONSTRAINT "user_garments_updated_by_fkey" FOREIGN KEY ("updated_by") REFERENCES "public"."admins"("id");



ALTER TABLE ONLY "public"."user_garments"
    ADD CONSTRAINT "user_garments_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE CASCADE;



GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";



GRANT ALL ON TABLE "public"."admins" TO "anon";
GRANT ALL ON TABLE "public"."admins" TO "authenticated";
GRANT ALL ON TABLE "public"."admins" TO "service_role";



GRANT ALL ON SEQUENCE "public"."admins_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."admins_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."admins_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."body_measurements" TO "anon";
GRANT ALL ON TABLE "public"."body_measurements" TO "authenticated";
GRANT ALL ON TABLE "public"."body_measurements" TO "service_role";



GRANT ALL ON SEQUENCE "public"."body_measurements_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."body_measurements_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."body_measurements_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."brands" TO "anon";
GRANT ALL ON TABLE "public"."brands" TO "authenticated";
GRANT ALL ON TABLE "public"."brands" TO "service_role";



GRANT ALL ON SEQUENCE "public"."brands_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."brands_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."brands_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."categories" TO "anon";
GRANT ALL ON TABLE "public"."categories" TO "authenticated";
GRANT ALL ON TABLE "public"."categories" TO "service_role";



GRANT ALL ON SEQUENCE "public"."categories_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."categories_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."categories_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."feedback_codes" TO "anon";
GRANT ALL ON TABLE "public"."feedback_codes" TO "authenticated";
GRANT ALL ON TABLE "public"."feedback_codes" TO "service_role";



GRANT ALL ON SEQUENCE "public"."feedback_codes_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."feedback_codes_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."feedback_codes_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."fit_zones" TO "anon";
GRANT ALL ON TABLE "public"."fit_zones" TO "authenticated";
GRANT ALL ON TABLE "public"."fit_zones" TO "service_role";



GRANT ALL ON SEQUENCE "public"."fit_zones_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."fit_zones_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."fit_zones_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."raw_size_guides" TO "anon";
GRANT ALL ON TABLE "public"."raw_size_guides" TO "authenticated";
GRANT ALL ON TABLE "public"."raw_size_guides" TO "service_role";



GRANT ALL ON SEQUENCE "public"."raw_size_guides_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."raw_size_guides_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."raw_size_guides_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."size_guide_entries" TO "anon";
GRANT ALL ON TABLE "public"."size_guide_entries" TO "authenticated";
GRANT ALL ON TABLE "public"."size_guide_entries" TO "service_role";



GRANT ALL ON SEQUENCE "public"."size_guide_entries_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."size_guide_entries_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."size_guide_entries_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."size_guides" TO "anon";
GRANT ALL ON TABLE "public"."size_guides" TO "authenticated";
GRANT ALL ON TABLE "public"."size_guides" TO "service_role";



GRANT ALL ON SEQUENCE "public"."size_guides_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."size_guides_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."size_guides_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."standardization_log" TO "anon";
GRANT ALL ON TABLE "public"."standardization_log" TO "authenticated";
GRANT ALL ON TABLE "public"."standardization_log" TO "service_role";



GRANT ALL ON SEQUENCE "public"."standardization_log_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."standardization_log_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."standardization_log_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."subcategories" TO "anon";
GRANT ALL ON TABLE "public"."subcategories" TO "authenticated";
GRANT ALL ON TABLE "public"."subcategories" TO "service_role";



GRANT ALL ON SEQUENCE "public"."subcategories_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."subcategories_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."subcategories_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."user_garment_feedback" TO "anon";
GRANT ALL ON TABLE "public"."user_garment_feedback" TO "authenticated";
GRANT ALL ON TABLE "public"."user_garment_feedback" TO "service_role";



GRANT ALL ON SEQUENCE "public"."user_garment_feedback_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."user_garment_feedback_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."user_garment_feedback_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."user_garments" TO "anon";
GRANT ALL ON TABLE "public"."user_garments" TO "authenticated";
GRANT ALL ON TABLE "public"."user_garments" TO "service_role";



GRANT ALL ON SEQUENCE "public"."user_garments_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."user_garments_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."user_garments_id_seq" TO "service_role";



GRANT ALL ON TABLE "public"."users" TO "anon";
GRANT ALL ON TABLE "public"."users" TO "authenticated";
GRANT ALL ON TABLE "public"."users" TO "service_role";



GRANT ALL ON SEQUENCE "public"."users_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."users_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."users_id_seq" TO "service_role";



ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "service_role";






ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "service_role";






RESET ALL;
