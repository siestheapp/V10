# Supabase Database Connection Guide

This guide explains how to connect to the Freestyle Supabase database using both MCP (Model Context Protocol) and psql.

---

## 🔗 Connection String

```
postgres://postgres:efvTower1211@db.ymncgfobqwhkekbydyjx.supabase.co:6543/postgres
```

### Connection Details
- **Host**: `db.ymncgfobqwhkekbydyjx.supabase.co`
- **Port**: `6543` (Supabase transaction mode)
- **Database**: `postgres`
- **User**: `postgres`
- **Password**: `efvTower1211`

---

## 🤖 MCP (Model Context Protocol) Setup

### Configuration File Location
`~/.cursor/mcp.json`

### Configuration
```json
{
  "mcpServers": {
    "freestylydb": {
      "command": "/Users/seandavey/.local/bin/postgres-mcp",
      "args": [
        "postgres://postgres:efvTower1211@db.ymncgfobqwhkekbydyjx.supabase.co:6543/postgres",
        "--access-mode",
        "restricted",
        "--transport",
        "stdio"
      ]
    }
  }
}
```

### Available MCP Commands in Cursor
- `/db list tables` - List all tables in the database
- `/db describe table <table_name>` - Get table structure and details
- Use MCP tools directly for read-only queries

### MCP Limitations
- **Read-only access** - Cannot create tables, insert data, or modify schema
- Use psql for write operations

---

## 💻 psql CLI Access

### Basic Connection
```bash
psql "postgres://postgres:efvTower1211@db.ymncgfobqwhkekbydyjx.supabase.co:6543/postgres"
```

### Running Single Commands
```bash
psql "postgres://postgres:efvTower1211@db.ymncgfobqwhkekbydyjx.supabase.co:6543/postgres" -c "YOUR SQL COMMAND HERE"
```

### Examples

#### List all schemas
```bash
psql "postgres://postgres:efvTower1211@db.ymncgfobqwhkekbydyjx.supabase.co:6543/postgres" -c "\dn"
```

#### List tables in public schema
```bash
psql "postgres://postgres:efvTower1211@db.ymncgfobqwhkekbydyjx.supabase.co:6543/postgres" -c "\dt public.*"
```

#### Create a schema
```bash
psql "postgres://postgres:efvTower1211@db.ymncgfobqwhkekbydyjx.supabase.co:6543/postgres" -c "CREATE SCHEMA demo AUTHORIZATION postgres;"
```

#### Copy table structure
```bash
psql "postgres://postgres:efvTower1211@db.ymncgfobqwhkekbydyjx.supabase.co:6543/postgres" -c "CREATE TABLE demo.brand (LIKE public.brand INCLUDING ALL);"
```

#### Run multiple commands
```bash
psql "postgres://postgres:efvTower1211@db.ymncgfobqwhkekbydyjx.supabase.co:6543/postgres" -c "
  CREATE TABLE demo.brand (LIKE public.brand INCLUDING ALL);
  CREATE TABLE demo.category (LIKE public.category INCLUDING ALL);
  CREATE TABLE demo.style (LIKE public.style INCLUDING ALL);
"
```

---

## 📊 Database Schema Overview

### Main Schemas
- **public** - Application tables (21 tables including brand, style, variant, etc.)
- **auth** - Supabase authentication tables (17 tables)
- **storage** - Supabase storage tables (7 tables)
- **demo** - Demo/testing schema (mirrors public schema structure, no data)

### Key Public Schema Tables
- `brand` - Brand information
- `brand_profile` - Brand profiles
- `category` - Product categories
- `style` - Product styles
- `variant` - Product variants
- `variant_code` - Variant codes
- `product_image` - Product images
- `product_url` - Product URLs
- `media_asset` - Media assets
- `color_catalog` - Color catalog
- `fabric_catalog` - Fabric catalog
- `fit_catalog` - Fit catalog
- `price_history` - Price tracking
- `inventory_history` - Inventory tracking
- `ingestion_job` - Data ingestion jobs
- `ingest_run` - Ingestion runs
- `evidence` - Evidence records

---

## 🎯 Common Use Cases

### When to Use MCP
- Quick table structure lookups
- Read-only queries
- Exploring the database schema
- Getting table relationships and indexes

### When to Use psql
- Creating or modifying schemas
- Creating or altering tables
- Inserting, updating, or deleting data
- Running migrations
- Bulk operations
- Any write operations

---

## 🔒 Security Notes

⚠️ **Important**: This connection string contains credentials and should be kept secure. The credentials are:
- Stored in `~/.cursor/mcp.json` (local machine only)
- Not committed to git repositories
- Used for development/testing purposes

---

## 📝 Quick Reference

### Cursor Terminal psql command
```bash
psql "postgres://postgres:efvTower1211@db.ymncgfobqwhkekbydyjx.supabase.co:6543/postgres" -c "YOUR_SQL_HERE"
```

### Check current database
```bash
psql "postgres://postgres:efvTower1211@db.ymncgfobqwhkekbydyjx.supabase.co:6543/postgres" -c "SELECT current_database(), current_schema(), current_user;"
```

### Interactive psql session
```bash
psql "postgres://postgres:efvTower1211@db.ymncgfobqwhkekbydyjx.supabase.co:6543/postgres"
```

---

## 🚀 Demo Schema Setup (Completed)

The `demo` schema has been created with:

### Tables
- `demo.brand` - Brand data (5 rows)
- `demo.category` - Categories (5 rows)
- `demo.style` - Styles (20 rows)
- `demo.variant` - Variants (40 rows)
- `demo.variant_code` - Variant codes
- `demo.product_image` - Product images
- `demo.user_profile` - Demo user profiles
- `demo.user_owned_variant` - User ownership tracking

### Views
- `demo.v_latest_price` - Latest prices per variant
- `demo.v_variant_image` - Representative images per variant
- `demo.v_proxy_feed` - Proxy feed for size twins

### Functions
- `demo.canonicalize_url(text)` - URL normalization
- `demo.find_variant_by_url(text)` - Resolve URL to variant ID

### RPC Functions (for Expo app)
- `demo.api_signup(p_username)` - Create demo user
- `demo.api_resolve_by_url(p_url)` - Resolve product URL to variant
- `demo.api_claim(p_user_id, p_variant_id, p_size_label, p_url)` - Claim ownership
- `demo.api_feed(p_user_id)` - Get proxy feed for user

All RPC functions are granted to `anon` role for safe use from mobile app.

### RLS Policies
Row Level Security is enabled with permissive policies for demo tables:
- `demo.user_profile` - Open read/insert for anon
- `demo.user_owned_variant` - Open read/insert for anon

These can be used for testing without affecting production data.

