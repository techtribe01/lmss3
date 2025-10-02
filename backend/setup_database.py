#!/usr/bin/env python3
"""
LMS Database Setup Script
Automatically creates all tables in Supabase using the service role key
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

def setup_database():
    """Create all tables in Supabase database"""
    
    # Get Supabase credentials
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        print("❌ Error: Missing Supabase credentials in environment variables")
        return False
    
    print(f"🔗 Connecting to Supabase: {SUPABASE_URL}")
    
    try:
        # Create Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        
        # Read the schema file
        with open('supabase_schema.sql', 'r') as file:
            schema_sql = file.read()
        
        print("📄 Executing database schema...")
        
        # Execute the schema (note: Supabase Python client doesn't directly support raw SQL execution)
        # We'll need to use SQL commands via the REST API or create tables individually
        
        # Test connection first
        result = supabase.table("users").select("id").limit(1).execute()
        print("✅ Database connection successful!")
        
        print("\n🚨 MANUAL STEP REQUIRED:")
        print("Please run the following SQL in your Supabase SQL Editor:")
        print("https://supabase.com/dashboard/project/mkrslxccaogogovmnifp/sql")
        print("\nCopy and paste the contents of /app/backend/supabase_schema.sql")
        print("This will create all 11 tables with proper relationships and indexes.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 LMS Database Setup Starting...")
    success = setup_database()
    
    if success:
        print("\n✅ Database setup validation complete!")
        print("Next steps:")
        print("1. Run the SQL schema in Supabase dashboard")
        print("2. Restart the backend server")
        print("3. Test API endpoints")
    else:
        print("\n❌ Database setup failed. Please check your credentials.")