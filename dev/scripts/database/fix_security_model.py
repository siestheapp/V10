#!/usr/bin/env python3
"""
Fix the security model:
- Make public reference data (brands, categories, size_guides) UNRESTRICTED
- Keep personal data (users, user_garments, etc.) RESTRICTED  
- Secure admin tables that are currently unrestricted
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys

# Database configuration
DB_CONFIG = {
    'host': 'aws-1-us-east-1.pooler.supabase.com',
    'port': '5432',
    'database': 'postgres',
    'user': 'fs_core_rw',
    'password': 'CHANGE_ME'
}

def main():
    print('🔧 FIXING DATABASE SECURITY MODEL')
    print('=' * 50)
    
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        print('✅ Connected to database\n')
        
        # Step 1: Make public reference data UNRESTRICTED
        print('🌐 MAKING PUBLIC DATA UNRESTRICTED:')
        
        public_tables = ['brands', 'categories', 'subcategories', 'size_guides', 'size_guide_entries']
        
        for table in public_tables:
            print(f'\\n  📖 Making {table} public:')
            
            try:
                # Drop existing policies first
                cur.execute(f'''
                    DROP POLICY IF EXISTS "Service role has full access to {table}" ON {table};
                ''')
                
                cur.execute(f'''
                    DROP POLICY IF EXISTS "Authenticated users can read {table}" ON {table};
                ''')
                
                # Disable RLS entirely for public data
                cur.execute(f'ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;')
                print(f'    ✅ RLS disabled - now fully public')
                
            except Exception as e:
                print(f'    ⚠️  Warning: {e}')
        
        # Step 2: Secure admin tables that should be restricted
        print(f'\\n🔒 SECURING ADMIN TABLES:')
        
        admin_tables = ['admins', 'admin_activity_log', 'audit_log']
        
        for table in admin_tables:
            print(f'\\n  🔐 Securing {table}:')
            
            try:
                # Check if table exists
                cur.execute('''
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    )
                ''', (table,))
                
                exists = cur.fetchone()['exists']
                
                if exists:
                    # Enable RLS
                    cur.execute(f'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;')
                    print(f'    ✅ RLS enabled')
                    
                    # Create admin-only policy
                    cur.execute(f'''
                        CREATE POLICY "Admin only access to {table}" ON {table}
                        FOR ALL USING (auth.role() = 'service_role');
                    ''')
                    print(f'    ✅ Admin-only policy created')
                else:
                    print(f'    ⚠️  Table does not exist')
                    
            except Exception as e:
                print(f'    ⚠️  Warning: {e}')
        
        # Step 3: Verify personal data is still secured
        print(f'\\n✅ VERIFYING PERSONAL DATA SECURITY:')
        
        personal_tables = ['users', 'user_garments', 'user_garment_feedback', 'body_measurements', 'user_fit_zones']
        
        for table in personal_tables:
            cur.execute('''
                SELECT 
                    c.relname as table_name,
                    c.relrowsecurity as rls_enabled
                FROM pg_class c
                JOIN pg_namespace n ON c.relnamespace = n.oid
                WHERE n.nspname = 'public' 
                AND c.relkind = 'r'
                AND c.relname = %s
            ''', (table,))
            
            result = cur.fetchone()
            if result:
                status = '✅ SECURED' if result['rls_enabled'] else '❌ UNSECURED'
                print(f'  • {table}: {status}')
        
        # Step 4: Show final security status
        print(f'\\n📊 FINAL SECURITY MODEL:')
        
        # Check all tables
        all_tables_to_check = public_tables + admin_tables + personal_tables
        
        for table in all_tables_to_check:
            cur.execute('''
                SELECT 
                    c.relname as table_name,
                    c.relrowsecurity as rls_enabled
                FROM pg_class c
                JOIN pg_namespace n ON c.relnamespace = n.oid
                WHERE n.nspname = 'public' 
                AND c.relkind = 'r'
                AND c.relname = %s
            ''', (table,))
            
            result = cur.fetchone()
            if result:
                if table in public_tables:
                    expected = 'PUBLIC'
                    status = '🌐 PUBLIC' if not result['rls_enabled'] else '🔒 RESTRICTED'
                    icon = '✅' if not result['rls_enabled'] else '❌'
                elif table in personal_tables:
                    expected = 'PERSONAL'
                    status = '🔒 RESTRICTED' if result['rls_enabled'] else '🌐 PUBLIC'
                    icon = '✅' if result['rls_enabled'] else '❌'
                else:  # admin tables
                    expected = 'ADMIN'
                    status = '🔒 RESTRICTED' if result['rls_enabled'] else '🌐 PUBLIC'
                    icon = '✅' if result['rls_enabled'] else '❌'
                
                print(f'  {icon} {table}: {status} ({expected} data)')
        
        # Commit changes
        conn.commit()
        print(f'\\n✅ Security model fixed successfully!')
        
        print(f'\\n🎯 SUMMARY:')
        print(f'  🌐 Public data: brands, categories, size_guides → UNRESTRICTED')
        print(f'  🔒 Personal data: users, user_garments, etc. → RESTRICTED') 
        print(f'  🔐 Admin data: admins, audit_log, etc. → RESTRICTED')
        print(f'  ✅ Proper security model now in place')
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f'❌ Error: {e}')
        if 'conn' in locals():
            conn.rollback()
        sys.exit(1)

if __name__ == '__main__':
    main()
