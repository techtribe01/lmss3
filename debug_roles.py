#!/usr/bin/env python3

import os
from supabase import create_client, Client

# Initialize Supabase client
url = "https://mkrslxccaogogovmnifp.supabase.co"
service_role_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1rcnNseGNjYW9nb2dvdm1uaWZwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTM4MTg1OCwiZXhwIjoyMDc0OTU3ODU4fQ.AgE6zKJsjJQ6tAk_Z_UFCsEh6h-TLU8r2oL_W3SekGM"

try:
    supabase: Client = create_client(url, service_role_key)
    print("✅ Supabase connection successful")
    
    # Check users in auth.users table
    print("\n🔍 Checking auth.users (authentication records)...")
    # Note: We can't directly query auth.users with the service role for security reasons
    # But we can check our custom users table
    
    print("\n🔍 Checking public.users (custom users table)...")
    result = supabase.table("users").select("*").execute()
    
    if result.data:
        print(f"Found {len(result.data)} users:")
        for user in result.data:
            print(f"  📧 {user.get('email', 'N/A')} | Role: {user.get('role', 'N/A')} | Username: {user.get('username', 'N/A')}")
    else:
        print("No users found in custom users table")
    
    # Check if the test accounts exist
    test_accounts = [
        "admin@lms.com", 
        "mentor@lms.com", 
        "student@lms.com",
        "mentor0001@lms.com",
        "mentor123@lms.com"
    ]
    
    print("\n🎯 Checking specific test accounts:")
    for email in test_accounts:
        result = supabase.table("users").select("*").eq("email", email).execute()
        if result.data:
            user = result.data[0]
            print(f"  ✅ {email} -> Role: {user.get('role', 'MISSING')}")
        else:
            print(f"  ❌ {email} -> NOT FOUND")

except Exception as e:
    print(f"❌ Error: {str(e)}")