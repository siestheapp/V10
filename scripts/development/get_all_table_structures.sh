#!/bin/bash

# Database connection details
DB_HOST="aws-0-us-east-2.pooler.supabase.com"
DB_PORT="6543"
DB_USER="postgres.lbilxlkchzpducggkrxx"
DB_NAME="postgres"
DB_PASSWORD="efvTower12"

# Export password for psql
export PGPASSWORD=$DB_PASSWORD

# Get list of tables (excluding system tables)
TABLES=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "
SELECT tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename NOT LIKE 'auth_%' 
AND tablename NOT LIKE 'realtime_%' 
AND tablename NOT LIKE 'storage_%' 
AND tablename NOT LIKE 'graphql_%' 
AND tablename NOT LIKE 'pgbouncer_%' 
AND tablename NOT LIKE 'supabase_migrations_%' 
AND tablename NOT LIKE 'vault_%' 
AND tablename NOT LIKE 'extensions_%'
ORDER BY tablename;")

echo "# Tailor3 Database Schema - Complete Table Structure"
echo ""
echo "## Database: tailor3 (Supabase)"
echo ""
echo "**Connection Details:**"
echo "- Host: $DB_HOST:$DB_PORT"
echo "- Database: $DB_NAME"
echo "- User: $DB_USER"
echo ""
echo "---"
echo ""

# Process each table
for table in $TABLES; do
    # Clean up table name (remove whitespace)
    table=$(echo $table | xargs)
    
    echo "## Table: \`$table\`"
    echo ""
    
    # Get table structure
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "\d $table" | while read line; do
        if [[ $line =~ ^[[:space:]]*[a-zA-Z_][a-zA-Z0-9_]*[[:space:]]+\|[[:space:]]+[a-zA-Z] ]]; then
            # Extract column name and type
            column=$(echo "$line" | awk -F'|' '{print $1}' | xargs)
            type=$(echo "$line" | awk -F'|' '{print $2}' | xargs)
            nullable=$(echo "$line" | awk -F'|' '{print $3}' | xargs)
            default=$(echo "$line" | awk -F'|' '{print $4}' | xargs)
            
            # Format the output
            nullable_text=""
            if [[ $nullable == "not null" ]]; then
                nullable_text=" (NOT NULL)"
            fi
            
            default_text=""
            if [[ $default != "" && $default != " " ]]; then
                default_text=" (DEFAULT: $default)"
            fi
            
            echo "- \`$column\` ($type)$nullable_text$default_text"
        fi
    done
    
    echo ""
    
    # Get constraints
    echo "**Constraints:**"
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "\d $table" | grep -E "(PRIMARY KEY|FOREIGN KEY|CHECK|UNIQUE)" | while read line; do
        if [[ $line =~ .* ]]; then
            echo "- $line"
        fi
    done
    
    echo ""
    echo "---"
    echo ""
done 