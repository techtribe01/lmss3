"""
Script to set up Supabase database schema
Run this once to create all tables
"""
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Read the SQL schema file
with open('supabase_schema.sql', 'r') as f:
    sql_commands = f.read()

print("=" * 80)
print("SUPABASE DATABASE SETUP")
print("=" * 80)
print("\nPlease execute the following SQL commands in your Supabase SQL Editor:")
print("\n1. Go to your Supabase project: https://supabase.com/dashboard/project/mkrslxccaogogovmnifp")
print("2. Navigate to 'SQL Editor' in the left sidebar")
print("3. Click 'New Query'")
print("4. Copy and paste the SQL from 'supabase_schema.sql' file")
print("5. Click 'Run' to execute")
print("\n" + "=" * 80)
print("\nSQL Schema File: /app/backend/supabase_schema.sql")
print("\nAfter running the SQL, you can test the setup with:")
print("  python setup_supabase.py --test")
print("\n" + "=" * 80)

# Test connection
def test_connection():
    try:
        print("\n🔍 Testing Supabase connection...")
        result = supabase.table("users").select("count", count="exact").execute()
        print(f"✅ Connection successful! Users table exists.")
        print(f"   Current user count: {result.count}")
        return True
    except Exception as e:
        print(f"❌ Connection test failed: {str(e)}")
        print("\nMake sure you have run the SQL schema in Supabase SQL Editor!")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_connection()
    else:
        print("\nTo test the connection after setting up the database:")
        print("  python setup_supabase.py --test")
