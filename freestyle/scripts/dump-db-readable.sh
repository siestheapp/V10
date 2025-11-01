#!/usr/bin/env bash
set -euo pipefail

# Full human-readable dump of a Postgres database using psql pretty-printed tables.
# - Includes all non-system schemas (excludes pg_catalog, information_schema, pg_toast)
# - Prints each table with a header showing row count and then full contents
# - Requires: psql

usage() {
  cat <<'USAGE'
Usage: dump-db-readable.sh [-u DATABASE_URL] [-o OUTPUT_FILE]

Options:
  -u  Postgres connection URL. Defaults to $DATABASE_URL if set,
      else the connection from DATABASE_CONNECTION_GUIDE.md
  -o  Output file path. Defaults to db-dumps/freestyledb_readable_dump_YYYYMMDD_HHMMSS.txt

Notes:
  - This prints aligned tables (ASCII boxes) for readability.
  - It may be very large for big databases.
USAGE
}

DATABASE_URL_DEFAULT="postgres://postgres:efvTower1211@db.ymncgfobqwhkekbydyjx.supabase.co:6543/postgres"
DB_URL="${DATABASE_URL:-}"
OUT=""

while getopts ":u:o:h" opt; do
  case $opt in
    u) DB_URL="$OPTARG" ;;
    o) OUT="$OPTARG" ;;
    h) usage; exit 0 ;;
    :) echo "Option -$OPTARG requires an argument." >&2; usage; exit 1 ;;
    \?) echo "Invalid option: -$OPTARG" >&2; usage; exit 1 ;;
  esac
done

if [[ -z "$DB_URL" ]]; then
  DB_URL="$DATABASE_URL_DEFAULT"
fi

if ! command -v psql >/dev/null 2>&1; then
  echo "psql is required but not found on PATH" >&2
  exit 1
fi

timestamp() {
  date +%Y%m%d_%H%M%S
}

if [[ -z "$OUT" ]]; then
  mkdir -p db-dumps
  OUT="db-dumps/freestyledb_readable_dump_$(timestamp).txt"
else
  mkdir -p "$(dirname "$OUT")"
fi

PSQL_BASE=(psql -X -q -v ON_ERROR_STOP=1 --set=pager=off "$DB_URL")

echo "Generating human-readable dump to: $OUT" >&2
{
  echo "============================="
  echo " Freestyle DB Readable Dump"
  echo "============================="
  echo
  echo "-- Connection"
  "${PSQL_BASE[@]}" -t -A -c "select 'database='||current_database()||', user='||current_user||', time='||now();"
  echo

  echo "-- Schemas (excluding system schemas)"
  "${PSQL_BASE[@]}" -c "select nspname as schema from pg_namespace where nspname not in ('pg_catalog','information_schema','pg_toast') order by 1;"
  echo

  SCHEMAS_RAW=$("${PSQL_BASE[@]}" -t -A -c "select nspname from pg_namespace where nspname not in ('pg_catalog','information_schema','pg_toast') order by 1;")
  IFS=$'\n' SCHEMAS=($SCHEMAS_RAW)
  unset IFS

  for schema in "${SCHEMAS[@]}"; do
    echo
    echo "============================="
    echo " Schema: $schema"
    echo "============================="
    echo

    # Tables
    declare -a TABLES=()
    TABLES_RAW=$("${PSQL_BASE[@]}" -t -A -c "select tablename from pg_tables where schemaname='"$schema"' order by 1;")
    IFS=$'\n' TABLES=($TABLES_RAW)
    unset IFS
    if [ -n "$TABLES_RAW" ]; then
      echo "-- Tables in $schema"
      "${PSQL_BASE[@]}" -c "select tablename from pg_tables where schemaname='"$schema"' order by 1;"
      echo
    fi

    for table in "${TABLES[@]}"; do
      # Count rows
      count=$("${PSQL_BASE[@]}" -t -A -c "select count(*) from \"$schema\".\"$table\";" || echo "0")
      echo
      echo "-- $schema.$table ($count records)"
      # Pretty print full table
      "${PSQL_BASE[@]}" -c "select * from \"$schema\".\"$table\";" || echo "(failed to query $schema.$table)"
    done

    # Views (optional, print data if simple)
    declare -a VIEWS=()
    VIEWS_RAW=$("${PSQL_BASE[@]}" -t -A -c "select viewname from pg_views where schemaname='"$schema"' order by 1;")
    IFS=$'\n' VIEWS=($VIEWS_RAW)
    unset IFS
    if [ -n "$VIEWS_RAW" ]; then
      echo
      echo "-- Views in $schema"
      "${PSQL_BASE[@]}" -c "select viewname from pg_views where schemaname='"$schema"' order by 1;"
      echo
    fi
    for view in "${VIEWS[@]}"; do
      echo
      echo "-- $schema.$view (view preview, first 200 rows)"
      "${PSQL_BASE[@]}" -c "select * from \"$schema\".\"$view\" limit 200;" || echo "(failed to query view $schema.$view)"
    done
  done
} > "$OUT"

echo "Done: $OUT" >&2


