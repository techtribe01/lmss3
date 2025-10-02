"""
Automated script to create Supabase tables using REST API
"""
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import requests

load_dotenv()

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

def execute_sql(sql: str):
    """Execute SQL using Supabase REST API"""
    url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json={"query": sql})
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

def create_tables_programmatically():
    """Create tables using individual SQL statements"""
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    print("🚀 Creating Supabase tables programmatically...")
    print("=" * 80)
    
    # List of SQL statements to execute
    sql_statements = [
        # Enable UUID extension
        'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"',
        
        # Users table
        '''CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'mentor', 'student')),
            phone VARCHAR(20),
            device_fingerprint TEXT,
            two_factor_enabled BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )''',
    ]
    
    # Note: Supabase doesn't allow direct SQL execution via REST API for DDL
    # We need to use the Supabase dashboard SQL editor
    
    print("⚠️  Unable to execute SQL programmatically.")
    print("📋 Please run the SQL manually in Supabase dashboard:")
    print("\n1. Open: https://supabase.com/dashboard/project/mkrslxccaogogovmnifp/sql")
    print("2. Copy the content from: /app/backend/supabase_schema.sql")
    print("3. Paste and run in SQL Editor")
    print("\nAfter running, test with: python create_tables.py --test")
    
def test_tables():
    """Test if tables exist"""
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    print("\n🔍 Testing Supabase tables...")
    print("=" * 80)
    
    tables_to_test = [
        "users", "courses", "enrollments", "attendance", "tasks",
        "task_submissions", "mock_interviews", "reports", 
        "fee_reminders", "materials", "certificates"
    ]
    
    all_exists = True
    for table in tables_to_test:
        try:
            result = supabase.table(table).select("*", count="exact").limit(0).execute()
            print(f"✅ {table:20} - Table exists (rows: {result.count})")
        except Exception as e:
            print(f"❌ {table:20} - Table missing or error: {str(e)[:50]}")
            all_exists = False
    
    print("=" * 80)
    if all_exists:
        print("✅ All tables created successfully!")
    else:
        print("⚠️  Some tables are missing. Please run the SQL schema.")
    
    return all_exists

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_tables()
    else:
        create_tables_programmatically()
