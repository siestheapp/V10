--
-- PostgreSQL database dump
--

-- Dumped from database version 14.16 (Homebrew)
-- Dumped by pg_dump version 14.16 (Homebrew)

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

--
-- Name: recalculate_fit_zones(); Type: FUNCTION; Schema: public; Owner: seandavey
--

CREATE FUNCTION public.recalculate_fit_zones() RETURNS trigger
    LANGUAGE plpgsql
    AS $_$
BEGIN
    -- Calculate average measurements for each fit type
    WITH measurements AS (
        SELECT 
            CASE 
                WHEN ug.chest_range ~ '^[0-9]+(\.[0-9]+)?-[0-9]+(\.[0-9]+)?$' THEN 
                    (CAST(split_part(ug.chest_range, '-', 1) AS FLOAT) + 
                     CAST(split_part(ug.chest_range, '-', 2) AS FLOAT)) / 2
                ELSE CAST(ug.chest_range AS FLOAT)
            END as chest_value,
            COALESCE(uff.chest_fit, ug.fit_feedback) as fit_type
        FROM user_garments ug
        LEFT JOIN user_fit_feedback uff ON ug.id = uff.garment_id
        WHERE ug.user_id = NEW.user_id
        AND ug.owns_garment = true
        AND ug.chest_range IS NOT NULL
    ),
    averages AS (
        SELECT 
            AVG(chest_value) FILTER (WHERE fit_type = 'Tight but I Like It') as tight_avg,
            AVG(chest_value) FILTER (WHERE fit_type = 'Good Fit') as good_avg,
            AVG(chest_value) FILTER (WHERE fit_type = 'Loose but I Like It') as loose_avg
        FROM measurements
    )
    -- Insert or update the fit zones
    INSERT INTO user_fit_zones (
        user_id, 
        category,
        tight_min,
        perfect_min,
        perfect_max,
        relaxed_max
    )
    SELECT 
        NEW.user_id,
        'Tops',
        CASE WHEN tight_avg IS NOT NULL THEN tight_avg * 0.97 ELSE NULL END,
        CASE WHEN good_avg IS NOT NULL THEN good_avg * 0.97 ELSE 40.0 END,
        CASE WHEN good_avg IS NOT NULL THEN good_avg * 1.03 ELSE 42.0 END,
        CASE WHEN loose_avg IS NOT NULL THEN loose_avg * 1.03 ELSE NULL END
    FROM averages
    ON CONFLICT (user_id, category) 
    DO UPDATE SET
        tight_min = EXCLUDED.tight_min,
        perfect_min = EXCLUDED.perfect_min,
        perfect_max = EXCLUDED.perfect_max,
        relaxed_max = EXCLUDED.relaxed_max;
    
    RETURN NEW;
END;
$_$;


ALTER FUNCTION public.recalculate_fit_zones() OWNER TO seandavey;

--
-- Name: refresh_metadata_on_alter_table(); Type: FUNCTION; Schema: public; Owner: seandavey
--

CREATE FUNCTION public.refresh_metadata_on_alter_table() RETURNS event_trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE database_metadata
    SET columns = (
        SELECT jsonb_agg(column_name)
        FROM information_schema.columns
        WHERE table_name = database_metadata.table_name
    );
END;
$$;


ALTER FUNCTION public.refresh_metadata_on_alter_table() OWNER TO seandavey;

--
-- Name: sync_fit_feedback(); Type: FUNCTION; Schema: public; Owner: seandavey
--

CREATE FUNCTION public.sync_fit_feedback() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE user_garments
    SET fit_feedback = CASE 
        WHEN NEW.overall_fit = 'Good Fit' THEN 'Good Fit'  -- Use 'Good Fit' instead of 'Perfect Fit'
        ELSE NEW.overall_fit
    END
    WHERE id = NEW.garment_id;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.sync_fit_feedback() OWNER TO seandavey;

--
-- Name: update_metadata_columns(); Type: FUNCTION; Schema: public; Owner: seandavey
--

CREATE FUNCTION public.update_metadata_columns() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE database_metadata
    SET columns = (
        SELECT jsonb_agg(column_name)
        FROM information_schema.columns
        WHERE table_name = NEW.table_name
    )
    WHERE table_name = NEW.table_name;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_metadata_columns() OWNER TO seandavey;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: automap; Type: TABLE; Schema: public; Owner: seandavey
--

CREATE TABLE public.automap (
    id integer NOT NULL,
    raw_term text NOT NULL,
    standardized_term text NOT NULL,
    transform_factor numeric DEFAULT 1,
    CONSTRAINT automap_standardized_term_check CHECK ((standardized_term = ANY (ARRAY['Chest'::text, 'Sleeve Length'::text, 'Waist'::text, 'Neck'::text])))
);


ALTER TABLE public.automap OWNER TO seandavey;

--
-- Name: automap_id_seq; Type: SEQUENCE; Schema: public; Owner: seandavey
--

CREATE SEQUENCE public.automap_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.automap_id_seq OWNER TO seandavey;

--
-- Name: automap_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: seandavey
--

ALTER SEQUENCE public.automap_id_seq OWNED BY public.automap.id;


--
-- Name: brand_automap; Type: TABLE; Schema: public; Owner: seandavey
--

CREATE TABLE public.brand_automap (
    id integer NOT NULL,
    raw_term text NOT NULL,
    standardized_term text NOT NULL,
    transform_factor numeric DEFAULT 1,
    mapped_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    brand_id integer
);


ALTER TABLE public.brand_automap OWNER TO seandavey;

--
-- Name: brand_automap_id_seq; Type: SEQUENCE; Schema: public; Owner: seandavey
--

CREATE SEQUENCE public.brand_automap_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.brand_automap_id_seq OWNER TO seandavey;

--
-- Name: brand_automap_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: seandavey
--

ALTER SEQUENCE public.brand_automap_id_seq OWNED BY public.brand_automap.id;


--
-- Name: brands; Type: TABLE; Schema: public; Owner: seandavey
--

CREATE TABLE public.brands (
    id integer NOT NULL,
    name text NOT NULL,
    default_unit text DEFAULT 'in'::text,
    size_guide_url text,
    CONSTRAINT brands_default_unit_check CHECK ((default_unit = ANY (ARRAY['in'::text, 'cm'::text])))
);


ALTER TABLE public.brands OWNER TO seandavey;

--
-- Name: brands_id_seq; Type: SEQUENCE; Schema: public; Owner: seandavey
--

CREATE SEQUENCE public.brands_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.brands_id_seq OWNER TO seandavey;

--
-- Name: brands_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: seandavey
--

ALTER SEQUENCE public.brands_id_seq OWNED BY public.brands.id;


--
-- Name: database_metadata; Type: TABLE; Schema: public; Owner: seandavey
--

CREATE TABLE public.database_metadata (
    id integer NOT NULL,
    table_name text NOT NULL,
    description text NOT NULL,
    columns jsonb
);


ALTER TABLE public.database_metadata OWNER TO seandavey;

--
-- Name: database_metadata_id_seq; Type: SEQUENCE; Schema: public; Owner: seandavey
--

CREATE SEQUENCE public.database_metadata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.database_metadata_id_seq OWNER TO seandavey;

--
-- Name: database_metadata_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: seandavey
--

ALTER SEQUENCE public.database_metadata_id_seq OWNED BY public.database_metadata.id;


--
-- Name: size_guide_mappings; Type: TABLE; Schema: public; Owner: seandavey
--

CREATE TABLE public.size_guide_mappings (
    id integer NOT NULL,
    brand text NOT NULL,
    size_guide_reference text NOT NULL,
    universal_category text NOT NULL
);


ALTER TABLE public.size_guide_mappings OWNER TO seandavey;

--
-- Name: size_guide_mappings_id_seq; Type: SEQUENCE; Schema: public; Owner: seandavey
--

CREATE SEQUENCE public.size_guide_mappings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.size_guide_mappings_id_seq OWNER TO seandavey;

--
-- Name: size_guide_mappings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: seandavey
--

ALTER SEQUENCE public.size_guide_mappings_id_seq OWNED BY public.size_guide_mappings.id;


--
-- Name: size_guide_sources; Type: TABLE; Schema: public; Owner: seandavey
--

CREATE TABLE public.size_guide_sources (
    id integer NOT NULL,
    brand text NOT NULL,
    category text NOT NULL,
    source_url text NOT NULL,
    retrieved_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    brand_id integer,
    original_category text
);


ALTER TABLE public.size_guide_sources OWNER TO seandavey;

--
-- Name: TABLE size_guide_sources; Type: COMMENT; Schema: public; Owner: seandavey
--

COMMENT ON TABLE public.size_guide_sources IS 'Stores the original source URLs for brand size guides for traceability.';


--
-- Name: size_guide_sources_id_seq; Type: SEQUENCE; Schema: public; Owner: seandavey
--

CREATE SEQUENCE public.size_guide_sources_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.size_guide_sources_id_seq OWNER TO seandavey;

--
-- Name: size_guide_sources_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: seandavey
--

ALTER SEQUENCE public.size_guide_sources_id_seq OWNED BY public.size_guide_sources.id;


--
-- Name: size_guides; Type: TABLE; Schema: public; Owner: seandavey
--

CREATE TABLE public.size_guides (
    id integer NOT NULL,
    brand text NOT NULL,
    gender text,
    category text NOT NULL,
    size_label text NOT NULL,
    chest_range text,
    sleeve_range text,
    waist_range text,
    unit text,
    brand_id integer,
    neck_range text,
    CONSTRAINT size_guides_gender_check CHECK ((gender = ANY (ARRAY['Men'::text, 'Women'::text, 'Unisex'::text]))),
    CONSTRAINT size_guides_unit_check CHECK ((unit = ANY (ARRAY['in'::text, 'cm'::text])))
);


ALTER TABLE public.size_guides OWNER TO seandavey;

--
-- Name: size_guides_id_seq; Type: SEQUENCE; Schema: public; Owner: seandavey
--

CREATE SEQUENCE public.size_guides_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.size_guides_id_seq OWNER TO seandavey;

--
-- Name: size_guides_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: seandavey
--

ALTER SEQUENCE public.size_guides_id_seq OWNED BY public.size_guides.id;


--
-- Name: universal_categories; Type: TABLE; Schema: public; Owner: seandavey
--

CREATE TABLE public.universal_categories (
    id integer NOT NULL,
    category text NOT NULL
);


ALTER TABLE public.universal_categories OWNER TO seandavey;

--
-- Name: universal_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: seandavey
--

CREATE SEQUENCE public.universal_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.universal_categories_id_seq OWNER TO seandavey;

--
-- Name: universal_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: seandavey
--

ALTER SEQUENCE public.universal_categories_id_seq OWNED BY public.universal_categories.id;


--
-- Name: user_fit_feedback; Type: TABLE; Schema: public; Owner: seandavey
--

CREATE TABLE public.user_fit_feedback (
    id integer NOT NULL,
    user_id integer NOT NULL,
    garment_id integer NOT NULL,
    overall_fit text,
    chest_fit text,
    sleeve_fit text,
    neck_fit text,
    waist_fit text,
    brand_id integer,
    CONSTRAINT user_fit_feedback_chest_fit_check CHECK ((chest_fit = ANY (ARRAY['Good Fit'::text, 'Tight but I Like It'::text, 'Too Tight'::text, 'Loose but I Like It'::text, 'Too Loose'::text]))),
    CONSTRAINT user_fit_feedback_neck_fit_check CHECK ((neck_fit = ANY (ARRAY['Too Tight'::text, 'Good Fit'::text, 'Too Loose'::text]))),
    CONSTRAINT user_fit_feedback_overall_fit_check CHECK ((overall_fit = ANY (ARRAY['Good Fit'::text, 'Too Tight'::text, 'Too Loose'::text, 'Tight but I Like It'::text, 'Loose but I Like It'::text]))),
    CONSTRAINT user_fit_feedback_sleeve_fit_check CHECK ((sleeve_fit = ANY (ARRAY['Good Fit'::text, 'Tight but I Like It'::text, 'Too Tight'::text, 'Loose but I Like It'::text, 'Too Loose'::text]))),
    CONSTRAINT user_fit_feedback_waist_fit_check CHECK ((waist_fit = ANY (ARRAY['Too Tight'::text, 'Good Fit'::text, 'Loose but I Like It'::text, 'Too Loose'::text])))
);


ALTER TABLE public.user_fit_feedback OWNER TO seandavey;

--
-- Name: user_fit_feedback_id_seq; Type: SEQUENCE; Schema: public; Owner: seandavey
--

CREATE SEQUENCE public.user_fit_feedback_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_fit_feedback_id_seq OWNER TO seandavey;

--
-- Name: user_fit_feedback_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: seandavey
--

ALTER SEQUENCE public.user_fit_feedback_id_seq OWNED BY public.user_fit_feedback.id;


--
-- Name: user_fit_zones; Type: TABLE; Schema: public; Owner: seandavey
--

CREATE TABLE public.user_fit_zones (
    id integer NOT NULL,
    user_id integer NOT NULL,
    category text NOT NULL,
    tight_min numeric,
    good_min numeric,
    good_max numeric,
    relaxed_max numeric,
    tight_max numeric,
    relaxed_min numeric,
    CONSTRAINT user_fit_zones_category_check CHECK ((category = 'Tops'::text))
);


ALTER TABLE public.user_fit_zones OWNER TO seandavey;

--
-- Name: user_fit_zones_id_seq; Type: SEQUENCE; Schema: public; Owner: seandavey
--

CREATE SEQUENCE public.user_fit_zones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_fit_zones_id_seq OWNER TO seandavey;

--
-- Name: user_fit_zones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: seandavey
--

ALTER SEQUENCE public.user_fit_zones_id_seq OWNED BY public.user_fit_zones.id;


--
-- Name: user_garments; Type: TABLE; Schema: public; Owner: seandavey
--

CREATE TABLE public.user_garments (
    id integer NOT NULL,
    user_id integer NOT NULL,
    brand_id integer NOT NULL,
    category text NOT NULL,
    size_label text NOT NULL,
    chest_range text NOT NULL,
    fit_feedback text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    owns_garment boolean DEFAULT false NOT NULL,
    CONSTRAINT user_garments_category_check CHECK ((category = 'Tops'::text)),
    CONSTRAINT user_garments_fit_feedback_check CHECK ((fit_feedback = ANY (ARRAY['Too Tight'::text, 'Tight but I Like It'::text, 'Good Fit'::text, 'Loose but I Like It'::text, 'Too Loose'::text])))
);


ALTER TABLE public.user_garments OWNER TO seandavey;

--
-- Name: user_garments_id_seq; Type: SEQUENCE; Schema: public; Owner: seandavey
--

CREATE SEQUENCE public.user_garments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_garments_id_seq OWNER TO seandavey;

--
-- Name: user_garments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: seandavey
--

ALTER SEQUENCE public.user_garments_id_seq OWNED BY public.user_garments.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: seandavey
--

CREATE TABLE public.users (
    id integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    email text,
    gender text,
    unit_preference text DEFAULT 'in'::text,
    test_column text,
    CONSTRAINT users_gender_check CHECK ((gender = ANY (ARRAY['Men'::text, 'Women'::text, 'Unisex'::text]))),
    CONSTRAINT users_unit_preference_check CHECK ((unit_preference = ANY (ARRAY['in'::text, 'cm'::text])))
);


ALTER TABLE public.users OWNER TO seandavey;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: seandavey
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO seandavey;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: seandavey
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: automap id; Type: DEFAULT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.automap ALTER COLUMN id SET DEFAULT nextval('public.automap_id_seq'::regclass);


--
-- Name: brand_automap id; Type: DEFAULT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.brand_automap ALTER COLUMN id SET DEFAULT nextval('public.brand_automap_id_seq'::regclass);


--
-- Name: brands id; Type: DEFAULT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.brands ALTER COLUMN id SET DEFAULT nextval('public.brands_id_seq'::regclass);


--
-- Name: database_metadata id; Type: DEFAULT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.database_metadata ALTER COLUMN id SET DEFAULT nextval('public.database_metadata_id_seq'::regclass);


--
-- Name: size_guide_mappings id; Type: DEFAULT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.size_guide_mappings ALTER COLUMN id SET DEFAULT nextval('public.size_guide_mappings_id_seq'::regclass);


--
-- Name: size_guide_sources id; Type: DEFAULT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.size_guide_sources ALTER COLUMN id SET DEFAULT nextval('public.size_guide_sources_id_seq'::regclass);


--
-- Name: size_guides id; Type: DEFAULT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.size_guides ALTER COLUMN id SET DEFAULT nextval('public.size_guides_id_seq'::regclass);


--
-- Name: universal_categories id; Type: DEFAULT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.universal_categories ALTER COLUMN id SET DEFAULT nextval('public.universal_categories_id_seq'::regclass);


--
-- Name: user_fit_feedback id; Type: DEFAULT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.user_fit_feedback ALTER COLUMN id SET DEFAULT nextval('public.user_fit_feedback_id_seq'::regclass);


--
-- Name: user_fit_zones id; Type: DEFAULT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.user_fit_zones ALTER COLUMN id SET DEFAULT nextval('public.user_fit_zones_id_seq'::regclass);


--
-- Name: user_garments id; Type: DEFAULT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.user_garments ALTER COLUMN id SET DEFAULT nextval('public.user_garments_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: automap; Type: TABLE DATA; Schema: public; Owner: seandavey
--

COPY public.automap (id, raw_term, standardized_term, transform_factor) FROM stdin;
1	Hip	Waist	1
2	Arm Length	Sleeve Length	1
4	Neck	Neck	1
\.


--
-- Data for Name: brand_automap; Type: TABLE DATA; Schema: public; Owner: seandavey
--

COPY public.brand_automap (id, raw_term, standardized_term, transform_factor, mapped_at, brand_id) FROM stdin;
3	Body Width	Chest	1	2025-02-16 22:29:01.556297	1
4	Half Chest Width	Chest	2	2025-02-16 22:29:01.556297	1
5	Hip	Waist	1	2025-02-16 22:29:01.556297	2
6	Arm Length	Sleeve Length	1	2025-02-16 22:29:01.556297	2
7	Outerwear	Tops	1	2025-02-16 22:29:01.556297	3
8	Shirts & Sweaters	Tops	1	2025-02-17 21:40:41.081715	9
9	Belt	Waist	1	2025-02-17 23:26:33.44104	9
\.


--
-- Data for Name: brands; Type: TABLE DATA; Schema: public; Owner: seandavey
--

COPY public.brands (id, name, default_unit, size_guide_url) FROM stdin;
1	Lululemon	in	https://shop.lululemon.com/help/size-guide/mens
2	Patagonia	in	https://www.patagonia.com/guides/size-fit/mens/
3	Theory	in	https://www.theory.com/size-guide/
7	J.Crew	in	https://www.jcrew.com/r/size-charts?srsltid=AfmBOopmMufU9TGhljM9Uk0INHw9FIiVM80iOcWazOFccAtoYsziUaW0
8	Faherty	in	https://fahertybrand.com/pages/mens-size-guide?srsltid=AfmBOop_QDvYGoAM1pPTD4GNS5JLAADZeK8a06Zmm2xE-ZfEF6PuYavg
9	Banana Republic	in	https://bananarepublic.gap.com/browse/info.do?cid=35404
\.


--
-- Data for Name: database_metadata; Type: TABLE DATA; Schema: public; Owner: seandavey
--

COPY public.database_metadata (id, table_name, description, columns) FROM stdin;
2	size_guides	Stores raw size guide data from brands, mapped to universal categories.	["brand_id", "id", "gender", "category", "size_label", "chest_range", "sleeve_range", "waist_range", "unit", "neck_range", "brand"]
10	user_fit_zones	Stores personalized fit zones for users, based on their past feedback.	["relaxed_min", "user_id", "id", "tight_min", "good_min", "good_max", "relaxed_max", "tight_max", "category"]
7	size_guide_sources	Stores references to size guide sources, including URLs for traceability.	["retrieved_at", "brand_id", "id", "original_category", "source_url", "brand", "category"]
3	fit_zones	Stores user fit preferences for recommendations.	\N
9	user_fit_feedback	Tracks user feedback on fit (e.g., "Too Tight", "Perfect Fit", "Too Loose").	["id", "user_id", "garment_id", "brand_id", "chest_fit", "sleeve_fit", "neck_fit", "waist_fit", "overall_fit"]
5	automap	Stores mappings of raw size guide terms to standardized terms.	["id", "transform_factor", "raw_term", "standardized_term"]
1	brands	Stores metadata about brands, including default unit and size guide URL.	["id", "name", "default_unit", "size_guide_url"]
11	user_garments	Stores garments a user has scanned or added for fit tracking.	["id", "user_id", "brand_id", "created_at", "owns_garment", "chest_range", "fit_feedback", "category", "size_label"]
4	size_guide_mappings	Maps brand-specific size guides to universal garment categories.	["id", "brand", "size_guide_reference", "universal_category"]
8	universal_categories	Stores standardized category names that all size guides map into.	["id", "category"]
12	users	Stores user accounts, including measurement profiles and preferences.	["id", "created_at", "email", "gender", "unit_preference", "test_column"]
6	brand_automap	Stores brand-specific term mappings for size guide standardization.	["id", "transform_factor", "mapped_at", "brand_id", "raw_term", "standardized_term"]
\.


--
-- Data for Name: size_guide_mappings; Type: TABLE DATA; Schema: public; Owner: seandavey
--

COPY public.size_guide_mappings (id, brand, size_guide_reference, universal_category) FROM stdin;
1	Lululemon	Lululemon Tops Size Guide	Tops
2	Patagonia	Patagonia Tops Size Guide	Tops
3	Theory	Theory Outerwear Size Guide	Tops
\.


--
-- Data for Name: size_guide_sources; Type: TABLE DATA; Schema: public; Owner: seandavey
--

COPY public.size_guide_sources (id, brand, category, source_url, retrieved_at, brand_id, original_category) FROM stdin;
3	Theory	Tops	https://example.com/theory-outerwear-size-guide	2025-02-17 18:53:33.516316	3	Outerwear
1	Patagonia	Tops	https://www.patagonia.com/guides/size-fit/mens/	2025-02-16 22:19:43.145262	2	Tops
2	Lululemon	Tops	https://shop.lululemon.com/help/size-guide/mens	2025-02-16 22:19:43.145262	1	Tops
4	Theory	Tops	https://www.theory.com/size-guide-page.html?srsltid=AfmBOor-EsoFfSxtOuTQaqJNLgI7GkzH1lXInwS22yot4wMxLLpWKfMA	2025-02-17 21:28:26.238059	3	Outerwear
6	J.Crew	Tops	https://www.jcrew.com/r/size-charts?srsltid=AfmBOopmMufU9TGhljM9Uk0INHw9FIiVM80iOcWazOFccAtoYsziUaW0	2025-02-17 21:33:39.213231	7	Tops
7	Faherty	Tops	https://fahertybrand.com/pages/mens-size-guide?srsltid=AfmBOop_QDvYGoAM1pPTD4GNS5JLAADZeK8a06Zmm2xE-ZfEF6PuYavg	2025-02-17 21:38:24.38961	8	Tops
8	Banana Republic	Tops	https://bananarepublic.gap.com/browse/info.do?cid=35404	2025-02-17 21:40:05.079615	9	Shirts & Sweaters
\.


--
-- Data for Name: size_guides; Type: TABLE DATA; Schema: public; Owner: seandavey
--

COPY public.size_guides (id, brand, gender, category, size_label, chest_range, sleeve_range, waist_range, unit, brand_id, neck_range) FROM stdin;
18	Theory	Men	Tops	XS	34.0-36.0	33.0-33.5	\N	in	3	\N
19	Theory	Men	Tops	S	36.0-38.0	33.5-34.0	\N	in	3	\N
20	Theory	Men	Tops	M	38.0-40.0	34.0-34.5	\N	in	3	\N
21	Theory	Men	Tops	L	40.0-42.0	34.5-35.0	\N	in	3	\N
22	Theory	Men	Tops	XL	42.0-44.0	35.0-35.5	\N	in	3	\N
23	Theory	Men	Tops	XXL	44.0-46.0	35.5-36.0	\N	in	3	\N
36	J.Crew	Men	Tops	XS	32-34	31-32	26-28	in	7	13-13.5
37	J.Crew	Men	Tops	S	35-37	32-33	29-31	in	7	14-14.5
38	J.Crew	Men	Tops	M	38-40	33-34	32-34	in	7	15-15.5
39	J.Crew	Men	Tops	L	41-43	34-35	35-37	in	7	16-16.5
40	J.Crew	Men	Tops	XL	44-46	35-36	38-40	in	7	17-17.5
41	J.Crew	Men	Tops	XXL	47-49	36-37	41-43	in	7	18-18.5
42	J.Crew	Men	Tops	XXXL	50-52	36-37	44-45	in	7	18-18.5
43	Faherty	Men	Tops	XS	34-36	32.5-33	26-28	in	8	14
44	Faherty	Men	Tops	S	37-39	32.5-34	28-30	in	8	14-14.5
45	Faherty	Men	Tops	M	40-41	34-35	31-33	in	8	15-15.5
46	Faherty	Men	Tops	L	42-44	35-36	34-36	in	8	16-16.5
47	Faherty	Men	Tops	XL	45-47	36-36.5	37-39	in	8	17-17.5
48	Faherty	Men	Tops	XXL	48-51	36.5-37	40-43	in	8	18-18.5
49	Faherty	Men	Tops	XXXL	52-54	37.5-38	44-47	in	8	19-19.5
50	Banana Republic	Men	Tops	XXS	32-33	31	25-26	in	9	13-13.5
51	Banana Republic	Men	Tops	XS	34-35	32	27-28	in	9	13-13.5
1	Lululemon	Men	Tops	XS	35-36	\N	\N	in	1	\N
2	Lululemon	Men	Tops	S	37-38	\N	\N	in	1	\N
3	Lululemon	Men	Tops	M	39-40	\N	\N	in	1	\N
4	Lululemon	Men	Tops	L	41-42	\N	\N	in	1	\N
5	Lululemon	Men	Tops	XL	43-45	\N	\N	in	1	\N
6	Lululemon	Men	Tops	XXL	46-48	\N	\N	in	1	\N
7	Lululemon	Men	Tops	3XL	50-52	\N	\N	in	1	\N
8	Lululemon	Men	Tops	4XL	53-55	\N	\N	in	1	\N
9	Lululemon	Men	Tops	5XL	56-58	\N	\N	in	1	\N
10	Patagonia	Men	Tops	XXS	33	30	32	in	2	\N
11	Patagonia	Men	Tops	XS	35	32	34	in	2	\N
12	Patagonia	Men	Tops	S	37	33	36	in	2	\N
13	Patagonia	Men	Tops	M	40	34	39	in	2	\N
14	Patagonia	Men	Tops	L	44	35	43	in	2	\N
15	Patagonia	Men	Tops	XL	47	36	46	in	2	\N
16	Patagonia	Men	Tops	XXL	50	37	49	in	2	\N
17	Patagonia	Men	Tops	XXXL	56	37.5	55	in	2	\N
52	Banana Republic	Men	Tops	S	36-37	33	29-31	in	9	14-14.5
53	Banana Republic	Men	Tops	M	38-40	34	32-33	in	9	15-15.5
54	Banana Republic	Men	Tops	L	41-44	35	34-35	in	9	16-16.5
55	Banana Republic	Men	Tops	XL	45-48	35.5	36-37	in	9	17-17.5
56	Banana Republic	Men	Tops	XXL	49-52	36	38-39	in	9	18-18.5
\.


--
-- Data for Name: universal_categories; Type: TABLE DATA; Schema: public; Owner: seandavey
--

COPY public.universal_categories (id, category) FROM stdin;
1	Tops
3	Jackets
4	Pants
\.


--
-- Data for Name: user_fit_feedback; Type: TABLE DATA; Schema: public; Owner: seandavey
--

COPY public.user_fit_feedback (id, user_id, garment_id, overall_fit, chest_fit, sleeve_fit, neck_fit, waist_fit, brand_id) FROM stdin;
3	1	1	Good Fit	Good Fit	\N	\N	\N	1
6	1	3	Loose but I Like It	Loose but I Like It	Loose but I Like It	\N	Loose but I Like It	2
8	1	7	Tight but I Like It	Tight but I Like It	\N	\N	\N	\N
\.


--
-- Data for Name: user_fit_zones; Type: TABLE DATA; Schema: public; Owner: seandavey
--

COPY public.user_fit_zones (id, user_id, category, tight_min, good_min, good_max, relaxed_max, tight_max, relaxed_min) FROM stdin;
1	1	Tops	37.0	39.5	39.5	47.0	37.0	47.0
\.


--
-- Data for Name: user_garments; Type: TABLE DATA; Schema: public; Owner: seandavey
--

COPY public.user_garments (id, user_id, brand_id, category, size_label, chest_range, fit_feedback, created_at, owns_garment) FROM stdin;
1	1	1	Tops	M	39-40	Good Fit	2025-02-17 23:52:16.031871	t
3	1	2	Tops	XL	47	Loose but I Like It	2025-02-18 00:22:32.857724	t
7	1	3	Tops	S	36.0-38.0	Tight but I Like It	2025-02-19 21:59:07.412855	t
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: seandavey
--

COPY public.users (id, created_at, email, gender, unit_preference, test_column) FROM stdin;
1	2025-02-17 23:48:08.770592	testuser@example.com	Men	in	\N
\.


--
-- Name: automap_id_seq; Type: SEQUENCE SET; Schema: public; Owner: seandavey
--

SELECT pg_catalog.setval('public.automap_id_seq', 4, true);


--
-- Name: brand_automap_id_seq; Type: SEQUENCE SET; Schema: public; Owner: seandavey
--

SELECT pg_catalog.setval('public.brand_automap_id_seq', 9, true);


--
-- Name: brands_id_seq; Type: SEQUENCE SET; Schema: public; Owner: seandavey
--

SELECT pg_catalog.setval('public.brands_id_seq', 9, true);


--
-- Name: database_metadata_id_seq; Type: SEQUENCE SET; Schema: public; Owner: seandavey
--

SELECT pg_catalog.setval('public.database_metadata_id_seq', 4, true);


--
-- Name: size_guide_mappings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: seandavey
--

SELECT pg_catalog.setval('public.size_guide_mappings_id_seq', 3, true);


--
-- Name: size_guide_sources_id_seq; Type: SEQUENCE SET; Schema: public; Owner: seandavey
--

SELECT pg_catalog.setval('public.size_guide_sources_id_seq', 8, true);


--
-- Name: size_guides_id_seq; Type: SEQUENCE SET; Schema: public; Owner: seandavey
--

SELECT pg_catalog.setval('public.size_guides_id_seq', 56, true);


--
-- Name: universal_categories_id_seq; Type: SEQUENCE SET; Schema: public; Owner: seandavey
--

SELECT pg_catalog.setval('public.universal_categories_id_seq', 11, true);


--
-- Name: user_fit_feedback_id_seq; Type: SEQUENCE SET; Schema: public; Owner: seandavey
--

SELECT pg_catalog.setval('public.user_fit_feedback_id_seq', 8, true);


--
-- Name: user_fit_zones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: seandavey
--

SELECT pg_catalog.setval('public.user_fit_zones_id_seq', 31, true);


--
-- Name: user_garments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: seandavey
--

SELECT pg_catalog.setval('public.user_garments_id_seq', 7, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: seandavey
--

SELECT pg_catalog.setval('public.users_id_seq', 1, true);


--
-- Name: automap automap_pkey; Type: CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.automap
    ADD CONSTRAINT automap_pkey PRIMARY KEY (id);


--
-- Name: automap automap_raw_term_key; Type: CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.automap
    ADD CONSTRAINT automap_raw_term_key UNIQUE (raw_term);


--
-- Name: brand_automap brand_automap_pkey; Type: CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.brand_automap
    ADD CONSTRAINT brand_automap_pkey PRIMARY KEY (id);


--
-- Name: brands brands_name_key; Type: CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.brands
    ADD CONSTRAINT brands_name_key UNIQUE (name);


--
-- Name: brands brands_pkey; Type: CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.brands
    ADD CONSTRAINT brands_pkey PRIMARY KEY (id);


--
-- Name: database_metadata database_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.database_metadata
    ADD CONSTRAINT database_metadata_pkey PRIMARY KEY (id);


--
-- Name: database_metadata database_metadata_table_name_key; Type: CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.database_metadata
    ADD CONSTRAINT database_metadata_table_name_key UNIQUE (table_name);


--
-- Name: size_guide_mappings size_guide_mappings_brand_size_guide_reference_universal_ca_key; Type: CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.size_guide_mappings
    ADD CONSTRAINT size_guide_mappings_brand_size_guide_reference_universal_ca_key UNIQUE (brand, size_guide_reference, universal_category);


--
-- Name: size_guide_mappings size_guide_mappings_pkey; Type: CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.size_guide_mappings
    ADD CONSTRAINT size_guide_mappings_pkey PRIMARY KEY (id);


--
-- Name: size_guide_sources size_guide_sources_brand_category_source_url_key; Type: CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.size_guide_sources
    ADD CONSTRAINT size_guide_sources_brand_category_source_url_key UNIQUE (brand, category, source_url);


--
-- Name: size_guide_sources size_guide_sources_pkey; Type: CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.size_guide_sources
    ADD CONSTRAINT size_guide_sources_pkey PRIMARY KEY (id);


--
-- Name: size_guides size_guides_pkey; Type: CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.size_guides
    ADD CONSTRAINT size_guides_pkey PRIMARY KEY (id);


--
-- Name: brand_automap unique_brand_term_mapping; Type: CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.brand_automap
    ADD CONSTRAINT unique_brand_term_mapping UNIQUE (brand_id, raw_term);


--
-- Name: size_guides unique_size_guide; Type: CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.size_guides
    ADD CONSTRAINT unique_size_guide UNIQUE (brand, gender, category, size_label);


--
-- Name: user_fit_zones unique_user_category; Type: CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.user_fit_zones
    ADD CONSTRAINT unique_user_category UNIQUE (user_id, category);


--
-- Name: user_fit_feedback unique_user_garment_feedback; Type: CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.user_fit_feedback
    ADD CONSTRAINT unique_user_garment_feedback UNIQUE (user_id, garment_id);


--
-- Name: universal_categories universal_categories_category_key; Type: CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.universal_categories
    ADD CONSTRAINT universal_categories_category_key UNIQUE (category);


--
-- Name: universal_categories universal_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.universal_categories
    ADD CONSTRAINT universal_categories_pkey PRIMARY KEY (id);


--
-- Name: user_fit_feedback user_fit_feedback_pkey; Type: CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.user_fit_feedback
    ADD CONSTRAINT user_fit_feedback_pkey PRIMARY KEY (id);


--
-- Name: user_fit_zones user_fit_zones_pkey; Type: CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.user_fit_zones
    ADD CONSTRAINT user_fit_zones_pkey PRIMARY KEY (id);


--
-- Name: user_garments user_garments_pkey; Type: CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.user_garments
    ADD CONSTRAINT user_garments_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: user_fit_feedback update_fit_zones; Type: TRIGGER; Schema: public; Owner: seandavey
--

CREATE TRIGGER update_fit_zones AFTER INSERT OR UPDATE ON public.user_fit_feedback FOR EACH ROW EXECUTE FUNCTION public.recalculate_fit_zones();


--
-- Name: user_fit_feedback update_garment_fit_feedback; Type: TRIGGER; Schema: public; Owner: seandavey
--

CREATE TRIGGER update_garment_fit_feedback AFTER INSERT OR UPDATE ON public.user_fit_feedback FOR EACH ROW EXECUTE FUNCTION public.sync_fit_feedback();


--
-- Name: brand_automap brand_automap_brand_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.brand_automap
    ADD CONSTRAINT brand_automap_brand_id_fkey FOREIGN KEY (brand_id) REFERENCES public.brands(id);


--
-- Name: size_guide_mappings size_guide_mappings_universal_category_fkey; Type: FK CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.size_guide_mappings
    ADD CONSTRAINT size_guide_mappings_universal_category_fkey FOREIGN KEY (universal_category) REFERENCES public.universal_categories(category);


--
-- Name: size_guide_sources size_guide_sources_brand_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.size_guide_sources
    ADD CONSTRAINT size_guide_sources_brand_id_fkey FOREIGN KEY (brand_id) REFERENCES public.brands(id);


--
-- Name: size_guides size_guides_brand_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.size_guides
    ADD CONSTRAINT size_guides_brand_id_fkey FOREIGN KEY (brand_id) REFERENCES public.brands(id);


--
-- Name: user_fit_feedback user_fit_feedback_garment_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.user_fit_feedback
    ADD CONSTRAINT user_fit_feedback_garment_id_fkey FOREIGN KEY (garment_id) REFERENCES public.user_garments(id);


--
-- Name: user_fit_feedback user_fit_feedback_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.user_fit_feedback
    ADD CONSTRAINT user_fit_feedback_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_fit_zones user_fit_zones_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.user_fit_zones
    ADD CONSTRAINT user_fit_zones_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_garments user_garments_brand_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.user_garments
    ADD CONSTRAINT user_garments_brand_id_fkey FOREIGN KEY (brand_id) REFERENCES public.brands(id);


--
-- Name: user_garments user_garments_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: seandavey
--

ALTER TABLE ONLY public.user_garments
    ADD CONSTRAINT user_garments_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: trigger_refresh_metadata; Type: EVENT TRIGGER; Schema: -; Owner: seandavey
--

CREATE EVENT TRIGGER trigger_refresh_metadata ON ddl_command_end
         WHEN TAG IN ('ALTER TABLE')
   EXECUTE FUNCTION public.refresh_metadata_on_alter_table();


ALTER EVENT TRIGGER trigger_refresh_metadata OWNER TO seandavey;

--
-- PostgreSQL database dump complete
--

