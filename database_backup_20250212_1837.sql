--
-- PostgreSQL database dump
--

-- Dumped from database version 14.15 (Homebrew)
-- Dumped by pg_dump version 14.15 (Homebrew)

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
-- Name: generate_tsin(); Type: FUNCTION; Schema: public; Owner: v10_user
--

CREATE FUNCTION public.generate_tsin() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
            BEGIN
                WITH item_count AS (
                    SELECT COUNT(*) + 1 as next_num 
                    FROM products 
                    WHERE brand = NEW.brand 
                    AND department = NEW.department
                )
                SELECT INTO NEW.tsin
                    CASE NEW.brand
                        WHEN 'Uniqlo' THEN 'U'
                    END ||
                    CASE NEW.department
                        WHEN 'Mens' THEN 'M'
                        WHEN 'Womens' THEN 'W'
                    END ||
                    CASE 
                        WHEN NEW.category IN ('Sweaters', 'T-Shirts', 'Shirts', 'Tops') THEN 'T'
                    END ||
                    COALESCE((SELECT next_num FROM item_count), 1)::text;
                
                RETURN NEW;
            END;
            $$;


ALTER FUNCTION public.generate_tsin() OWNER TO v10_user;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: click_tracking; Type: TABLE; Schema: public; Owner: v10_user
--

CREATE TABLE public.click_tracking (
    id integer NOT NULL,
    product_code character varying NOT NULL,
    user_id character varying,
    scanned_size character varying,
    clicked_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.click_tracking OWNER TO v10_user;

--
-- Name: click_tracking_id_seq; Type: SEQUENCE; Schema: public; Owner: v10_user
--

CREATE SEQUENCE public.click_tracking_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.click_tracking_id_seq OWNER TO v10_user;

--
-- Name: click_tracking_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: v10_user
--

ALTER SEQUENCE public.click_tracking_id_seq OWNED BY public.click_tracking.id;


--
-- Name: fit_feedback; Type: TABLE; Schema: public; Owner: v10_user
--

CREATE TABLE public.fit_feedback (
    id integer NOT NULL,
    user_id integer,
    brand_name character varying(100),
    garment_name character varying(255),
    size character varying(20),
    measurement_name character varying(100),
    feedback text,
    overall_feeling text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.fit_feedback OWNER TO v10_user;

--
-- Name: fit_feedback_id_seq; Type: SEQUENCE; Schema: public; Owner: v10_user
--

CREATE SEQUENCE public.fit_feedback_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fit_feedback_id_seq OWNER TO v10_user;

--
-- Name: fit_feedback_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: v10_user
--

ALTER SEQUENCE public.fit_feedback_id_seq OWNED BY public.fit_feedback.id;


--
-- Name: fit_ranges; Type: TABLE; Schema: public; Owner: v10_user
--

CREATE TABLE public.fit_ranges (
    id integer NOT NULL,
    user_id integer,
    measurement_type_id integer,
    good_fit_min numeric(10,2),
    good_fit_max numeric(10,2),
    tight_fit_min numeric(10,2),
    tight_fit_max numeric(10,2),
    loose_fit_min numeric(10,2),
    loose_fit_max numeric(10,2),
    absolute_min numeric(10,2),
    absolute_max numeric(10,2),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.fit_ranges OWNER TO v10_user;

--
-- Name: fit_ranges_id_seq; Type: SEQUENCE; Schema: public; Owner: v10_user
--

CREATE SEQUENCE public.fit_ranges_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fit_ranges_id_seq OWNER TO v10_user;

--
-- Name: fit_ranges_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: v10_user
--

ALTER SEQUENCE public.fit_ranges_id_seq OWNED BY public.fit_ranges.id;


--
-- Name: measurement_mappings; Type: TABLE; Schema: public; Owner: v10_user
--

CREATE TABLE public.measurement_mappings (
    id integer NOT NULL,
    measurement_type_id integer,
    brand_name character varying(100),
    original_name character varying(100) NOT NULL,
    measurement_method character varying(50),
    conversion_factor numeric(10,2),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.measurement_mappings OWNER TO v10_user;

--
-- Name: measurement_mappings_id_seq; Type: SEQUENCE; Schema: public; Owner: v10_user
--

CREATE SEQUENCE public.measurement_mappings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.measurement_mappings_id_seq OWNER TO v10_user;

--
-- Name: measurement_mappings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: v10_user
--

ALTER SEQUENCE public.measurement_mappings_id_seq OWNED BY public.measurement_mappings.id;


--
-- Name: measurement_types; Type: TABLE; Schema: public; Owner: v10_user
--

CREATE TABLE public.measurement_types (
    id integer NOT NULL,
    name character varying(50) NOT NULL,
    display_name character varying(50) NOT NULL,
    measurement_type character varying(20) NOT NULL,
    description text,
    unit character varying(10) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.measurement_types OWNER TO v10_user;

--
-- Name: measurement_types_id_seq; Type: SEQUENCE; Schema: public; Owner: v10_user
--

CREATE SEQUENCE public.measurement_types_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.measurement_types_id_seq OWNER TO v10_user;

--
-- Name: measurement_types_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: v10_user
--

ALTER SEQUENCE public.measurement_types_id_seq OWNED BY public.measurement_types.id;


--
-- Name: measurements; Type: TABLE; Schema: public; Owner: v10_user
--

CREATE TABLE public.measurements (
    product_code character varying NOT NULL,
    measurements jsonb NOT NULL
);


ALTER TABLE public.measurements OWNER TO v10_user;

--
-- Name: product_codes; Type: TABLE; Schema: public; Owner: v10_user
--

CREATE TABLE public.product_codes (
    alternate_code character varying NOT NULL,
    primary_code character varying
);


ALTER TABLE public.product_codes OWNER TO v10_user;

--
-- Name: products; Type: TABLE; Schema: public; Owner: v10_user
--

CREATE TABLE public.products (
    product_code character varying NOT NULL,
    name character varying NOT NULL,
    category character varying NOT NULL,
    subcategory character varying,
    image_url character varying,
    product_url character varying,
    brand character varying,
    brand_id integer,
    department character varying,
    tsin character varying(20)
);


ALTER TABLE public.products OWNER TO v10_user;

--
-- Name: scan_history; Type: TABLE; Schema: public; Owner: v10_user
--

CREATE TABLE public.scan_history (
    id integer NOT NULL,
    user_id character varying,
    product_code character varying NOT NULL,
    scanned_size character varying,
    scanned_price numeric(10,2),
    scanned_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.scan_history OWNER TO v10_user;

--
-- Name: scan_history_id_seq; Type: SEQUENCE; Schema: public; Owner: v10_user
--

CREATE SEQUENCE public.scan_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.scan_history_id_seq OWNER TO v10_user;

--
-- Name: scan_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: v10_user
--

ALTER SEQUENCE public.scan_history_id_seq OWNED BY public.scan_history.id;


--
-- Name: user_measurements; Type: TABLE; Schema: public; Owner: v10_user
--

CREATE TABLE public.user_measurements (
    id integer NOT NULL,
    user_id integer,
    measurement_type_id integer,
    value numeric(10,2) NOT NULL,
    original_value character varying(50),
    original_name character varying(100),
    confidence numeric(5,2),
    source_type character varying(50),
    product_code character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    brand_name character varying(100),
    garment_name character varying(255),
    size character varying(20),
    feedback text,
    owns_garment boolean,
    product_id character varying(100),
    value_min numeric(10,2),
    value_max numeric(10,2)
);


ALTER TABLE public.user_measurements OWNER TO v10_user;

--
-- Name: user_measurements_id_seq; Type: SEQUENCE; Schema: public; Owner: v10_user
--

CREATE SEQUENCE public.user_measurements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_measurements_id_seq OWNER TO v10_user;

--
-- Name: user_measurements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: v10_user
--

ALTER SEQUENCE public.user_measurements_id_seq OWNED BY public.user_measurements.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: v10_user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    password_hash text NOT NULL,
    name character varying(255),
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now()
);


ALTER TABLE public.users OWNER TO v10_user;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: v10_user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO v10_user;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: v10_user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: click_tracking id; Type: DEFAULT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.click_tracking ALTER COLUMN id SET DEFAULT nextval('public.click_tracking_id_seq'::regclass);


--
-- Name: fit_feedback id; Type: DEFAULT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.fit_feedback ALTER COLUMN id SET DEFAULT nextval('public.fit_feedback_id_seq'::regclass);


--
-- Name: fit_ranges id; Type: DEFAULT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.fit_ranges ALTER COLUMN id SET DEFAULT nextval('public.fit_ranges_id_seq'::regclass);


--
-- Name: measurement_mappings id; Type: DEFAULT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.measurement_mappings ALTER COLUMN id SET DEFAULT nextval('public.measurement_mappings_id_seq'::regclass);


--
-- Name: measurement_types id; Type: DEFAULT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.measurement_types ALTER COLUMN id SET DEFAULT nextval('public.measurement_types_id_seq'::regclass);


--
-- Name: scan_history id; Type: DEFAULT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.scan_history ALTER COLUMN id SET DEFAULT nextval('public.scan_history_id_seq'::regclass);


--
-- Name: user_measurements id; Type: DEFAULT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.user_measurements ALTER COLUMN id SET DEFAULT nextval('public.user_measurements_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: click_tracking; Type: TABLE DATA; Schema: public; Owner: v10_user
--

COPY public.click_tracking (id, product_code, user_id, scanned_size, clicked_at) FROM stdin;
\.


--
-- Data for Name: fit_feedback; Type: TABLE DATA; Schema: public; Owner: v10_user
--

COPY public.fit_feedback (id, user_id, brand_name, garment_name, size, measurement_name, feedback, overall_feeling, created_at) FROM stdin;
8	18	Lululemon	Evolution Long-Sleeve Polo Shirt	M	chest	Good fit	Good	2025-02-05 00:39:44.258625
9	18	Patagonia	Long-Sleeved Capilene Cool Daily Shirt	XL	chest	Loose fit	Loose	2025-02-05 00:39:44.258625
10	18	Banana Republic	Soft Wash Long-Sleeve T-Shirt	L	chest	Good fit	Good	2025-02-05 00:39:44.258625
11	18	Cos	MERINO WOOL HALF-ZIP POLO SHIRT	L	chest	Good fit	Good	2025-02-05 00:39:44.258625
12	18	J Crew	Cotton piqué-stitch crewneck sweater	L	chest	Good fit	Good	2025-02-05 00:39:44.258625
13	18	Theory	Brenan Polo Shirt	S	chest	Tight fit, good for polo style	Tight	2025-02-05 00:39:44.258625
14	18	Lacoste	Regular Fit Velour Shirt	42	chest	Loose fit	Loose	2025-02-05 00:39:44.258625
15	18	The Commons	100% cashmere quarter zip	L	chest	Good fit	Good	2025-02-05 00:39:44.258625
16	18	Reiss	V Neck Sweater	M	chest	Tight but acceptable	Tight	2025-02-05 00:39:44.258625
17	18	Reiss	Dress shirt	L	chest	Good fit	Good	2025-02-05 00:39:44.258625
18	18	Faherty	Long sleeve shirt	L	chest	Loose fit	Loose	2025-02-05 00:39:44.258625
1	18	Uniqlo	Brushed Cotton T-Shirt Long Sleeve	M	body_length	Too short	Too small	2025-02-04 00:44:28.595492
2	18	Uniqlo	Brushed Cotton T-Shirt Long Sleeve	L	body_length	Too long	Too big	2025-02-04 00:44:28.595492
3	18	Uniqlo	Brushed Cotton T-Shirt Long Sleeve	L	body_width	Too loose	Too big	2025-02-04 00:44:28.595492
4	18	Uniqlo	Waffle T-Shirt Long Sleeve	M	body_length	Good, hovers right over belt line	Too small	2025-02-04 00:44:28.595492
5	18	Uniqlo	Waffle T-Shirt Long Sleeve	M	shoulder_width	Too small	Too small	2025-02-04 00:44:28.595492
6	18	Uniqlo	Waffle T-Shirt Long Sleeve	L	body_length	Probably maximum length that fits, slightly baggy	Too big	2025-02-04 00:44:28.595492
7	18	Uniqlo	Waffle T-Shirt Long Sleeve	L	body_width	Too loose	Too big	2025-02-04 00:44:28.595492
\.


--
-- Data for Name: fit_ranges; Type: TABLE DATA; Schema: public; Owner: v10_user
--

COPY public.fit_ranges (id, user_id, measurement_type_id, good_fit_min, good_fit_max, tight_fit_min, tight_fit_max, loose_fit_min, loose_fit_max, absolute_min, absolute_max, created_at, updated_at) FROM stdin;
1	18	1	39.00	44.00	36.00	38.50	43.00	47.00	36.00	47.00	2025-02-11 00:47:10.880498	2025-02-11 00:47:10.880498
2	18	1	39.00	44.00	36.00	38.50	43.00	47.00	36.00	47.00	2025-02-11 01:03:59.419981	2025-02-11 01:03:59.419981
\.


--
-- Data for Name: measurement_mappings; Type: TABLE DATA; Schema: public; Owner: v10_user
--

COPY public.measurement_mappings (id, measurement_type_id, brand_name, original_name, measurement_method, conversion_factor, created_at) FROM stdin;
1	1	Uniqlo	body_width	half_measurement	2.00	2025-02-04 00:27:44.522438
2	2	Uniqlo	sleeve_length	from_center_back	1.00	2025-02-04 00:27:44.522438
3	4	Uniqlo	body_length_back	\N	1.00	2025-02-04 00:27:44.522438
4	5	Uniqlo	shoulder_width	\N	1.00	2025-02-04 00:27:44.522438
5	1	Uniqlo	sleeve_length	center_back	1.00	2025-02-04 00:33:07.291607
6	1	\N	Sleeve Length (Center Back)	center_back	1.00	2025-02-04 00:33:07.291607
7	2	\N	Sleeve	shoulder_to_wrist	1.18	2025-02-04 00:33:07.291607
8	2	\N	Arm length	shoulder_to_wrist	1.18	2025-02-04 00:33:07.291607
\.


--
-- Data for Name: measurement_types; Type: TABLE DATA; Schema: public; Owner: v10_user
--

COPY public.measurement_types (id, name, display_name, measurement_type, description, unit, created_at) FROM stdin;
1	chest_circumference	Chest	circumference	\N	inches	2025-02-04 00:27:38.757361
2	sleeve_length_cb	Sleeve Length (Center Back)	length	\N	inches	2025-02-04 00:27:38.757361
3	sleeve_length_shoulder	Sleeve Length (Shoulder)	length	\N	inches	2025-02-04 00:27:38.757361
4	body_length	Body Length	length	\N	inches	2025-02-04 00:27:38.757361
5	shoulder_width	Shoulder Width	width	\N	inches	2025-02-04 00:27:38.757361
8	neck_circumference	Neck	circumference	\N	inches	2025-02-10 23:01:11.387625
9	waist_circumference	Waist	circumference	\N	inches	2025-02-10 23:01:11.387625
\.


--
-- Data for Name: measurements; Type: TABLE DATA; Schema: public; Owner: v10_user
--

COPY public.measurements (product_code, measurements) FROM stdin;
475296	{"sizes": {"L": {"body_width": "20", "body_length": "28", "sleeve_length": "26"}, "M": {"body_width": "19", "body_length": "27", "sleeve_length": "25"}, "S": {"body_width": "18", "body_length": "26", "sleeve_length": "24"}, "XL": {"body_width": "21", "body_length": "29", "sleeve_length": "27"}, "XS": {"body_width": "17", "body_length": "25", "sleeve_length": "23"}}, "units": "inches"}
475352	{"sizes": {"L": {"body_width": "24", "sleeve_length": "34.5", "shoulder_width": "17.5", "body_length_back": "29"}, "M": {"body_width": "22", "sleeve_length": "33.5", "shoulder_width": "16.5", "body_length_back": "27.5"}, "S": {"body_width": "21", "sleeve_length": "32.5", "shoulder_width": "16", "body_length_back": "26.5"}, "XL": {"body_width": "25.5", "sleeve_length": "35", "shoulder_width": "18", "body_length_back": "30"}, "XS": {"body_width": "20", "sleeve_length": "31.5", "shoulder_width": "15.5", "body_length_back": "25.5"}}, "units": "inches", "measurement_type": "tops_with_shoulder"}
\.


--
-- Data for Name: product_codes; Type: TABLE DATA; Schema: public; Owner: v10_user
--

COPY public.product_codes (alternate_code, primary_code) FROM stdin;
469925	475352
466823	475352
460318	475352
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: v10_user
--

COPY public.products (product_code, name, category, subcategory, image_url, product_url, brand, brand_id, department, tsin) FROM stdin;
475352	Waffle T-Shirt | Long Sleeve	Tops	Long Sleeve	https://image.uniqlo.com/UQ/ST3/us/imagesgoods/475352/item/goods_09_475352.jpg	https://www.uniqlo.com/us/en/products/E460318-000/	Uniqlo	1	Mens	UMT2
475296	3D Knit Sweater	Sweaters	Crew Neck	https://image.uniqlo.com/UQ/ST3/us/imagesgoods/475296/item/475296_09_large.jpg	https://www.uniqlo.com/us/en/products/E475296-000/00	Uniqlo	1	Mens	UMT1
\.


--
-- Data for Name: scan_history; Type: TABLE DATA; Schema: public; Owner: v10_user
--

COPY public.scan_history (id, user_id, product_code, scanned_size, scanned_price, scanned_at) FROM stdin;
1	18	475296	L	49.90	2025-02-01 19:40:04.565729
2	18	475296	L	49.90	2025-02-01 19:50:41.053488
3	18	475296	L	49.90	2025-02-01 19:54:56.500513
4	18	475296	L	49.90	2025-02-01 19:56:49.818207
5	18	475296	L	49.90	2025-02-02 17:33:05.955162
6	18	475296	L	49.90	2025-02-02 17:37:40.571885
7	18	475296	L	49.90	2025-02-02 17:41:08.395782
8	18	475296	L	49.90	2025-02-02 20:16:48.966723
9	18	475352	\N	29.90	2025-02-02 21:41:28.160661
10	18	475352	\N	29.90	2025-02-02 22:10:32.592805
11	18	475352	Ch	29.90	2025-02-02 22:18:39.091963
12	18	475352	Ch	29.90	2025-02-02 22:20:26.73349
13	18	475352	\N	29.90	2025-02-02 22:30:26.369117
14	18	475352	\N	29.90	2025-02-02 22:31:48.88685
15	18	475352	\N	29.90	2025-02-02 22:36:16.425231
16	18	475352	\N	29.90	2025-02-02 22:38:16.160716
17	18	475352	\N	29.90	2025-02-02 22:40:20.452831
18	18	475352	\N	29.90	2025-02-02 22:42:31.105024
19	18	475352	L	29.90	2025-02-02 22:44:28.323734
20	18	475352	L	29.90	2025-02-04 00:12:44.744483
21	18	475352	L	29.90	2025-02-05 00:14:37.711998
22	18	475352	L	29.90	2025-02-05 00:31:05.752295
23	18	475352	L	29.90	2025-02-05 01:35:44.893761
24	18	475352	L	29.90	2025-02-05 16:44:16.283799
25	18	475352	L	29.90	2025-02-05 16:56:40.792104
26	18	475352	L	29.90	2025-02-05 16:58:52.191967
27	\N	475352	L	29.90	2025-02-10 21:54:36.919223
28	\N	475352	L	29.90	2025-02-10 21:56:30.824488
29	\N	475352	L	29.90	2025-02-10 22:03:54.198613
30	\N	475352	L	29.90	2025-02-11 00:47:53.612384
\.


--
-- Data for Name: user_measurements; Type: TABLE DATA; Schema: public; Owner: v10_user
--

COPY public.user_measurements (id, user_id, measurement_type_id, value, original_value, original_name, confidence, source_type, product_code, created_at, brand_name, garment_name, size, feedback, owns_garment, product_id, value_min, value_max) FROM stdin;
8	18	1	47.00	47.00	Chest	0.90	brand_size_guide	\N	2025-02-04 00:41:00.701452	Patagonia	Long-Sleeved Capilene Cool Daily Shirt	XL	\N	t	\N	47.00	47.00
25	18	1	43.00	43.00	Chest circumference	0.90	brand_size_guide	\N	2025-02-04 00:43:08.936926	Lacoste	Regular Fit Velour Shirt	42	\N	t	\N	43.00	43.00
28	18	4	30.20	30.20	Product Measurement - Front length	0.90	brand_size_guide	\N	2025-02-04 00:43:08.936926	Lacoste	Regular Fit Velour Shirt	42	\N	t	\N	30.20	30.20
32	18	1	38.50	38.50	Chest	0.90	brand_size_guide	\N	2025-02-04 00:43:08.936926	Reiss	V Neck Sweater	M	\N	t	\N	38.50	38.50
34	18	1	40.00	40.00	Chest	0.90	brand_size_guide	\N	2025-02-04 00:43:08.936926	Reiss	Dress shirt	L	\N	t	\N	40.00	40.00
1	18	1	41.00	20.50	Half Chest Width	0.90	brand_size_guide	\N	2025-02-04 00:40:09.344868	NN07	Clive Waffle knit Tee	M	\N	t	\N	41.00	41.00
2	18	1	41.00	20.50	Half Chest Width	0.90	brand_size_guide	\N	2025-02-04 00:41:00.701452	NN07	Clive Waffle knit Tee	M	\N	t	\N	41.00	41.00
3	18	4	27.00	27.00	Center Back Length	0.90	brand_size_guide	\N	2025-02-04 00:41:00.701452	NN07	Clive Waffle knit Tee	M	\N	t	\N	27.00	27.00
33	18	9	32.00	32.00	Waist	0.90	brand_size_guide	\N	2025-02-04 00:43:08.936926	Reiss	V Neck Sweater	M	\N	t	\N	32.00	32.00
6	18	1	39.00	99.00	Chest	0.90	brand_size_guide	\N	2025-02-04 00:41:00.701452	Knowledge Cotton Apparel	Long sleeve shirt green	M	\N	t	\N	39.00	39.00
19	18	4	27.50	27.50	Body length back	0.95	user_feedback	\N	2025-02-04 00:41:00.701452	Uniqlo	Waffle T-Shirt Long Sleeve	M	\N	f	\N	27.50	27.50
20	18	5	16.50	16.50	Shoulder width	0.95	user_feedback	\N	2025-02-04 00:41:00.701452	Uniqlo	Waffle T-Shirt Long Sleeve	M	\N	f	\N	16.50	16.50
21	18	1	44.00	22.00	Body width	0.95	user_feedback	\N	2025-02-04 00:41:00.701452	Uniqlo	Waffle T-Shirt Long Sleeve	M	\N	f	\N	44.00	44.00
36	18	4	29.50	29.50	Body length back	0.95	user_feedback	\N	2025-02-04 00:43:08.936926	Uniqlo	Brushed Cotton T-Shirt Long Sleeve	L	\N	f	\N	29.50	29.50
37	18	5	18.00	18.00	Shoulder width	0.95	user_feedback	\N	2025-02-04 00:43:08.936926	Uniqlo	Brushed Cotton T-Shirt Long Sleeve	L	\N	f	\N	18.00	18.00
38	18	1	47.00	23.50	Body width	0.95	user_feedback	\N	2025-02-04 00:43:08.936926	Uniqlo	Brushed Cotton T-Shirt Long Sleeve	L	\N	f	\N	47.00	47.00
27	18	2	26.40	26.40	Product Measurement - Sleeve length	0.90	brand_size_guide	\N	2025-02-04 00:43:08.936926	Lacoste	Regular Fit Velour Shirt	42	\N	t	\N	26.40	26.40
9	18	3	36.00	36.00	Arm length	0.90	brand_size_guide	\N	2025-02-04 00:41:00.701452	Patagonia	Long-Sleeved Capilene Cool Daily Shirt	XL	\N	t	\N	36.00	36.00
11	18	3	35.00	35.00	Sleeve	0.90	brand_size_guide	\N	2025-02-04 00:41:00.701452	Banana Republic	Soft Wash Long-Sleeve T-Shirt	L	\N	t	\N	35.00	35.00
4	18	3	26.00	26.00	Sleeve Length	0.90	brand_size_guide	\N	2025-02-04 00:41:00.701452	NN07	Clive Waffle knit Tee	M	\N	t	\N	26.00	26.00
12	18	8	16.25	16.25	Neck	0.90	brand_size_guide	\N	2025-02-04 00:41:00.701452	Banana Republic	Soft Wash Long-Sleeve T-Shirt	L	\N	t	\N	16.25	16.25
26	18	8	16.00	16.00	Neck circumference	0.90	brand_size_guide	\N	2025-02-04 00:43:08.936926	Lacoste	Regular Fit Velour Shirt	42	\N	t	\N	16.00	16.00
35	18	8	16.00	16.00	Collar size	0.90	brand_size_guide	\N	2025-02-04 00:43:08.936926	Reiss	Dress shirt	L	\N	t	\N	16.00	16.00
7	18	9	34.30	87.00	Waist	0.90	brand_size_guide	\N	2025-02-04 00:41:00.701452	Knowledge Cotton Apparel	Long sleeve shirt green	M	\N	t	\N	34.30	34.30
29	18	1	42.00	42.00	Chest	0.90	brand_size_guide	\N	2025-02-04 00:43:08.936926	The Commons	100% cashmere quarter zip	L	\N	t	\N	41.00	43.00
5	18	1	39.50	39-40	Your Chest	0.90	brand_size_guide	\N	2025-02-04 00:41:00.701452	Lululemon	Evolution Long-Sleeve Polo Shirt	M	\N	t	\N	39.00	40.00
10	18	1	42.50	41-44	Chest	0.90	brand_size_guide	\N	2025-02-04 00:41:00.701452	Banana Republic	Soft Wash Long-Sleeve T-Shirt	L	\N	t	\N	41.00	44.00
13	18	1	41.70	41.70	Chest	0.90	brand_size_guide	\N	2025-02-04 00:41:00.701452	Cos	MERINO WOOL HALF-ZIP POLO SHIRT	L	\N	t	\N	40.90	42.50
14	18	3	25.50	25.50	Arm length	0.90	brand_size_guide	\N	2025-02-04 00:41:00.701452	Cos	MERINO WOOL HALF-ZIP POLO SHIRT	L	\N	t	\N	40.90	42.50
15	18	1	42.00	42.00	Chest	0.90	brand_size_guide	\N	2025-02-04 00:41:00.701452	J Crew	Cotton piqué-stitch crewneck sweater	L	\N	t	\N	41.00	43.00
16	18	3	34.50	34.50	Arm length	0.90	brand_size_guide	\N	2025-02-04 00:41:00.701452	J Crew	Cotton piqué-stitch crewneck sweater	L	\N	t	\N	41.00	43.00
31	18	3	34.00	34.00	Arm length	0.90	brand_size_guide	\N	2025-02-04 00:43:08.936926	The Commons	100% cashmere quarter zip	L	\N	t	\N	41.00	43.00
30	18	8	16.25	16.25	Neck	0.90	brand_size_guide	\N	2025-02-04 00:43:08.936926	The Commons	100% cashmere quarter zip	L	\N	t	\N	41.00	43.00
17	18	1	44.00	44.00	Chest	0.90	brand_size_guide	\N	2025-02-04 00:41:00.701452	Faherty	Long sleeve shirt	L	\N	t	\N	43.00	45.00
18	18	3	35.50	35.50	Sleeve	0.90	brand_size_guide	\N	2025-02-04 00:41:00.701452	Faherty	Long sleeve shirt	L	\N	t	\N	43.00	45.00
22	18	1	37.00	37.00	Body Measurement - Chest	0.90	brand_size_guide	\N	2025-02-04 00:43:08.936926	Theory	Brenan Polo Shirt in Cotton-Linen	S	\N	t	\N	36.00	38.00
23	18	4	25.50	25.50	Product Measurement - Length	0.90	brand_size_guide	\N	2025-02-04 00:43:08.936926	Theory	Brenan Polo Shirt in Cotton-Linen	S	\N	t	\N	36.00	38.00
24	18	3	33.75	33.75	Body Measurement - Sleeve	0.90	brand_size_guide	\N	2025-02-04 00:43:08.936926	Theory	Brenan Polo Shirt in Cotton-Linen	S	\N	t	\N	36.00	38.00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: v10_user
--

COPY public.users (id, email, password_hash, name, created_at, updated_at) FROM stdin;
18	srdavey97@gmail.com	sies	user1	2025-02-05 00:39:36.292515	2025-02-05 00:39:36.292515
\.


--
-- Name: click_tracking_id_seq; Type: SEQUENCE SET; Schema: public; Owner: v10_user
--

SELECT pg_catalog.setval('public.click_tracking_id_seq', 1, false);


--
-- Name: fit_feedback_id_seq; Type: SEQUENCE SET; Schema: public; Owner: v10_user
--

SELECT pg_catalog.setval('public.fit_feedback_id_seq', 18, true);


--
-- Name: fit_ranges_id_seq; Type: SEQUENCE SET; Schema: public; Owner: v10_user
--

SELECT pg_catalog.setval('public.fit_ranges_id_seq', 2, true);


--
-- Name: measurement_mappings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: v10_user
--

SELECT pg_catalog.setval('public.measurement_mappings_id_seq', 8, true);


--
-- Name: measurement_types_id_seq; Type: SEQUENCE SET; Schema: public; Owner: v10_user
--

SELECT pg_catalog.setval('public.measurement_types_id_seq', 9, true);


--
-- Name: scan_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: v10_user
--

SELECT pg_catalog.setval('public.scan_history_id_seq', 30, true);


--
-- Name: user_measurements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: v10_user
--

SELECT pg_catalog.setval('public.user_measurements_id_seq', 38, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: v10_user
--

SELECT pg_catalog.setval('public.users_id_seq', 18, true);


--
-- Name: click_tracking click_tracking_pkey; Type: CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.click_tracking
    ADD CONSTRAINT click_tracking_pkey PRIMARY KEY (id);


--
-- Name: fit_feedback fit_feedback_pkey; Type: CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.fit_feedback
    ADD CONSTRAINT fit_feedback_pkey PRIMARY KEY (id);


--
-- Name: fit_ranges fit_ranges_pkey; Type: CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.fit_ranges
    ADD CONSTRAINT fit_ranges_pkey PRIMARY KEY (id);


--
-- Name: measurement_mappings measurement_mappings_pkey; Type: CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.measurement_mappings
    ADD CONSTRAINT measurement_mappings_pkey PRIMARY KEY (id);


--
-- Name: measurement_types measurement_types_name_key; Type: CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.measurement_types
    ADD CONSTRAINT measurement_types_name_key UNIQUE (name);


--
-- Name: measurement_types measurement_types_pkey; Type: CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.measurement_types
    ADD CONSTRAINT measurement_types_pkey PRIMARY KEY (id);


--
-- Name: measurements measurements_pkey; Type: CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.measurements
    ADD CONSTRAINT measurements_pkey PRIMARY KEY (product_code);


--
-- Name: product_codes product_codes_pkey; Type: CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.product_codes
    ADD CONSTRAINT product_codes_pkey PRIMARY KEY (alternate_code);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (product_code);


--
-- Name: scan_history scan_history_pkey; Type: CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.scan_history
    ADD CONSTRAINT scan_history_pkey PRIMARY KEY (id);


--
-- Name: user_measurements user_measurements_pkey; Type: CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.user_measurements
    ADD CONSTRAINT user_measurements_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: products set_tsin; Type: TRIGGER; Schema: public; Owner: v10_user
--

CREATE TRIGGER set_tsin BEFORE INSERT ON public.products FOR EACH ROW EXECUTE FUNCTION public.generate_tsin();


--
-- Name: click_tracking click_tracking_product_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.click_tracking
    ADD CONSTRAINT click_tracking_product_code_fkey FOREIGN KEY (product_code) REFERENCES public.products(product_code);


--
-- Name: fit_feedback fit_feedback_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.fit_feedback
    ADD CONSTRAINT fit_feedback_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: fit_ranges fit_ranges_measurement_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.fit_ranges
    ADD CONSTRAINT fit_ranges_measurement_type_id_fkey FOREIGN KEY (measurement_type_id) REFERENCES public.measurement_types(id);


--
-- Name: fit_ranges fit_ranges_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.fit_ranges
    ADD CONSTRAINT fit_ranges_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: measurement_mappings measurement_mappings_measurement_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.measurement_mappings
    ADD CONSTRAINT measurement_mappings_measurement_type_id_fkey FOREIGN KEY (measurement_type_id) REFERENCES public.measurement_types(id);


--
-- Name: measurements measurements_product_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.measurements
    ADD CONSTRAINT measurements_product_code_fkey FOREIGN KEY (product_code) REFERENCES public.products(product_code);


--
-- Name: product_codes product_codes_primary_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.product_codes
    ADD CONSTRAINT product_codes_primary_code_fkey FOREIGN KEY (primary_code) REFERENCES public.products(product_code);


--
-- Name: scan_history scan_history_product_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.scan_history
    ADD CONSTRAINT scan_history_product_code_fkey FOREIGN KEY (product_code) REFERENCES public.products(product_code);


--
-- Name: user_measurements user_measurements_measurement_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.user_measurements
    ADD CONSTRAINT user_measurements_measurement_type_id_fkey FOREIGN KEY (measurement_type_id) REFERENCES public.measurement_types(id);


--
-- Name: user_measurements user_measurements_product_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.user_measurements
    ADD CONSTRAINT user_measurements_product_code_fkey FOREIGN KEY (product_code) REFERENCES public.products(product_code);


--
-- Name: user_measurements user_measurements_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: v10_user
--

ALTER TABLE ONLY public.user_measurements
    ADD CONSTRAINT user_measurements_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: seandavey
--

ALTER DEFAULT PRIVILEGES FOR ROLE seandavey IN SCHEMA public GRANT ALL ON SEQUENCES  TO v10_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: seandavey
--

ALTER DEFAULT PRIVILEGES FOR ROLE seandavey IN SCHEMA public GRANT ALL ON TABLES  TO v10_user;


--
-- PostgreSQL database dump complete
--

