#!/usr/bin/env python3
"""
Database Schema Validation Test
Validates Supabase database connection and table structure
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv('/app/backend/.env')

def test_database_connection():
    """Test Supabase database connection and schema validation"""
    print("🔍 SUPABASE DATABASE VALIDATION")
    print("=" * 60)
    
    # Get Supabase credentials
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_SERVICE_ROLE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        print("❌ CRITICAL: Missing Supabase credentials")
        print(f"   SUPABASE_URL: {'✅ Set' if SUPABASE_URL else '❌ Missing'}")
        print(f"   SUPABASE_SERVICE_ROLE_KEY: {'✅ Set' if SUPABASE_SERVICE_ROLE_KEY else '❌ Missing'}")
        return False
    
    print("✅ Supabase credentials found")
    print(f"   URL: {SUPABASE_URL}")
    print(f"   Service Key: {SUPABASE_SERVICE_ROLE_KEY[:20]}...")
    
    try:
        # Create Supabase client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        print("✅ Supabase client created successfully")
        
        # Test connection by querying a simple table
        result = supabase.table("users").select("count", count="exact").execute()
        print(f"✅ Database connection successful - {result.count} users in database")
        
        # Validate all required tables exist
        required_tables = [
            "users", "courses", "enrollments", "attendance", "tasks", 
            "task_submissions", "mock_interviews", "reports", 
            "fee_reminders", "materials", "certificates"
        ]
        
        print("\n📋 Validating table structure...")
        for table in required_tables:
            try:
                result = supabase.table(table).select("count", count="exact").execute()
                print(f"✅ Table '{table}': {result.count} records")
            except Exception as e:
                print(f"❌ Table '{table}': Error - {str(e)}")
                return False
        
        print(f"\n🎉 All {len(required_tables)} tables validated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    exit(0 if success else 1)