#!/bin/bash

# Database connection details
DB_HOST="aws-0-us-east-2.pooler.supabase.com"
DB_PORT="6543"
DB_USER="postgres.lbilxlkchzpducggkrxx"
DB_NAME="postgres"
DB_PASSWORD="efvTower12"

# Export password for psql
export PGPASSWORD=$DB_PASSWORD

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

# Get list of tables
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

# Process each table
for table in $TABLES; do
    # Clean up table name
    table=$(echo $table | xargs)
    
    echo "## Table: \`$table\`"
    echo ""
    
    # Get detailed table structure
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "\d $table" > /tmp/table_structure.tmp
    
    # Extract columns
    echo "**Columns:**"
    cat /tmp/table_structure.tmp | awk '/^[[:space:]]*[a-zA-Z_][a-zA-Z0-9_]*[[:space:]]+\|[[:space:]]+[a-zA-Z]/ {
        column = $1
        type = $2
        nullable = $3
        default = $4
        
        nullable_text = ""
        if (nullable == "not null") {
            nullable_text = " (NOT NULL)"
        }
        
        default_text = ""
        if (default != "" && default != " ") {
            default_text = " (DEFAULT: " default ")"
        }
        
        print "- `" column "` (" type ")" nullable_text default_text
    }'
    
    echo ""
    echo "**Constraints:**"
    
    # Extract constraints
    cat /tmp/table_structure.tmp | grep -E "(PRIMARY KEY|FOREIGN KEY|CHECK|UNIQUE|REFERENCES)" | while read line; do
        if [[ $line =~ .* ]]; then
            echo "- $line"
        fi
    done
    
    # Get indexes
    echo ""
    echo "**Indexes:**"
    cat /tmp/table_structure.tmp | grep -E "(Indexes|btree|hash)" | while read line; do
        if [[ $line =~ .* ]]; then
            echo "- $line"
        fi
    done
    
    echo ""
    echo "---"
    echo ""
    
    # Clean up temp file
    rm /tmp/table_structure.tmp
done 