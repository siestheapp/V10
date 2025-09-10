#!/bin/bash

# Admin psql runner (direct, non-pooled)
# Usage examples:
#   scripts/database/psql_admin.sh -c "SELECT 1;"
#   scripts/database/psql_admin.sh -f scripts/database/migrations/20250814_add_set_methodology.sql

set -euo pipefail

: "${DB_HOST_DIRECT:?Set DB_HOST_DIRECT to your Supabase direct host (not the pooler host)}"
: "${DB_PORT_DIRECT:=5432}"
: "${DB_USER_DIRECT:?Set DB_USER_DIRECT to your direct DB user (e.g. postgres)}"
: "${DB_PASSWORD_DIRECT:?Set DB_PASSWORD_DIRECT to your direct DB password}"
: "${DB_NAME:=postgres}"

export PGPASSWORD="${DB_PASSWORD_DIRECT}"

psql \
  -h "${DB_HOST_DIRECT}" \
  -p "${DB_PORT_DIRECT}" \
  -U "${DB_USER_DIRECT}" \
  -d "${DB_NAME}" \
  -X -v ON_ERROR_STOP=1 "$@"


