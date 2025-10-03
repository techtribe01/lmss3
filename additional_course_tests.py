#!/usr/bin/env python3
"""
Additional Course Management Tests
Verify edge cases and data persistence
"""

import requests
import json
import sys

BACKEND_URL = "https://securelearn-4.preview.emergentagent.com/api"

def test_approval_workflow():
    """Test the complete approval workflow"""
    print("🔍 Testing Complete Approval Workflow...")
    
    # Create test users
    session = requests.Session()
    
    # Register admin and mentor
    admin_data = {
        "username": "workflow_admin",
        "email": "workflow_admin@test.com",
        "password": "admin123",
        "full_name": "Workflow Admin",
        "role": "admin"
    }
    
    mentor_data = {
        "username": "workflow_mentor",
        "email": "workflow_mentor@test.com", 
        "password": "mentor123",
        "full_name": "Workflow Mentor",
        "role": "mentor"
    }
    
    student_data = {
        "username": "workflow_student",
        "email": "workflow_student@test.com",
        "password": "student123", 
        "full_name": "Workflow Student",
        "role": "student"
    }
    
    # Register users
    admin_response = session.post(f"{BACKEND_URL}/auth/register", json=admin_data)
    mentor_response = session.post(f"{BACKEND_URL}/auth/register", json=mentor_data)
    student_response = session.post(f"{BACKEND_URL}/auth/register", json=student_data)
    
    if admin_response.status_code != 200 or mentor_response.status_code != 200 or student_response.status_code != 200:
        print("❌ Failed to register test users")
        return False
    
    admin_token = admin_response.json()["access_token"]
    mentor_token = mentor_response.json()["access_token"]
    student_token = student_response.json()["access_token"]
    
    # Step 1: Mentor creates a course (should be pending)
    course_data = {
        "title": "React Development Bootcamp",
        "description": "Complete React course from beginner to advanced",
        "zoom_id": "react-zoom-123"
    }
    
    mentor_headers = {"Authorization": f"Bearer {mentor_token}"}
    create_response = session.post(f"{BACKEND_URL}/courses", json=course_data, headers=mentor_headers)
    
    if create_response.status_code != 200:
        print("❌ Failed to create course")
        return False
    
    course = create_response.json()
    course_id = course["id"]
    
    # Verify course is pending
    if course["approval_status"] != "pending":
        print(f"❌ Expected pending status, got: {course['approval_status']}")
        return False
    
    print("✅ Step 1: Mentor created course with pending status")
    
    # Step 2: Student tries to access pending course (should fail)
    student_headers = {"Authorization": f"Bearer {student_token}"}
    student_access = session.get(f"{BACKEND_URL}/courses/{course_id}", headers=student_headers)
    
    if student_access.status_code != 403:
        print(f"❌ Expected 403 for student accessing pending course, got: {student_access.status_code}")
        return False
    
    print("✅ Step 2: Student correctly denied access to pending course")
    
    # Step 3: Student lists courses (should not see pending course)
    student_list = session.get(f"{BACKEND_URL}/courses", headers=student_headers)
    if student_list.status_code != 200:
        print("❌ Failed to list courses as student")
        return False
    
    student_courses = student_list.json()
    pending_courses = [c for c in student_courses if c["id"] == course_id]
    
    if len(pending_courses) > 0:
        print("❌ Student should not see pending courses in list")
        return False
    
    print("✅ Step 3: Student correctly does not see pending course in list")
    
    # Step 4: Admin approves the course
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    approval_data = {"approval_status": "approved"}
    approve_response = session.put(f"{BACKEND_URL}/courses/{course_id}/approve", json=approval_data, headers=admin_headers)
    
    if approve_response.status_code != 200:
        print("❌ Failed to approve course")
        return False
    
    approved_course = approve_response.json()
    if approved_course["approval_status"] != "approved":
        print(f"❌ Expected approved status, got: {approved_course['approval_status']}")
        return False
    
    print("✅ Step 4: Admin successfully approved course")
    
    # Step 5: Student can now access approved course
    student_access_approved = session.get(f"{BACKEND_URL}/courses/{course_id}", headers=student_headers)
    
    if student_access_approved.status_code != 200:
        print(f"❌ Expected 200 for student accessing approved course, got: {student_access_approved.status_code}")
        return False
    
    print("✅ Step 5: Student can now access approved course")
    
    # Step 6: Student can see approved course in list
    student_list_after = session.get(f"{BACKEND_URL}/courses", headers=student_headers)
    if student_list_after.status_code != 200:
        print("❌ Failed to list courses as student after approval")
        return False
    
    student_courses_after = student_list_after.json()
    approved_courses = [c for c in student_courses_after if c["id"] == course_id]
    
    if len(approved_courses) != 1:
        print("❌ Student should see approved course in list")
        return False
    
    print("✅ Step 6: Student can now see approved course in list")
    
    # Step 7: Test rejection workflow
    rejection_data = {"approval_status": "rejected"}
    reject_response = session.put(f"{BACKEND_URL}/courses/{course_id}/approve", json=rejection_data, headers=admin_headers)
    
    if reject_response.status_code != 200:
        print("❌ Failed to reject course")
        return False
    
    rejected_course = reject_response.json()
    if rejected_course["approval_status"] != "rejected":
        print(f"❌ Expected rejected status, got: {rejected_course['approval_status']}")
        return False
    
    print("✅ Step 7: Admin successfully rejected course")
    
    # Step 8: Student can no longer see rejected course
    student_list_rejected = session.get(f"{BACKEND_URL}/courses", headers=student_headers)
    if student_list_rejected.status_code != 200:
        print("❌ Failed to list courses as student after rejection")
        return False
    
    student_courses_rejected = student_list_rejected.json()
    rejected_courses = [c for c in student_courses_rejected if c["id"] == course_id]
    
    if len(rejected_courses) > 0:
        print("❌ Student should not see rejected course in list")
        return False
    
    print("✅ Step 8: Student correctly does not see rejected course")
    
    print("\n🎉 Complete approval workflow test PASSED!")
    return True

def test_mentor_access_control():
    """Test mentor access control for their own vs other mentors' courses"""
    print("\n🔍 Testing Mentor Access Control...")
    
    session = requests.Session()
    
    # Register two mentors
    mentor1_data = {
        "username": "mentor_one",
        "email": "mentor1@test.com",
        "password": "mentor123",
        "full_name": "Mentor One",
        "role": "mentor"
    }
    
    mentor2_data = {
        "username": "mentor_two", 
        "email": "mentor2@test.com",
        "password": "mentor123",
        "full_name": "Mentor Two", 
        "role": "mentor"
    }
    
    mentor1_response = session.post(f"{BACKEND_URL}/auth/register", json=mentor1_data)
    mentor2_response = session.post(f"{BACKEND_URL}/auth/register", json=mentor2_data)
    
    if mentor1_response.status_code != 200 or mentor2_response.status_code != 200:
        print("❌ Failed to register mentors")
        return False
    
    mentor1_token = mentor1_response.json()["access_token"]
    mentor2_token = mentor2_response.json()["access_token"]
    mentor1_id = mentor1_response.json()["user"]["id"]
    mentor2_id = mentor2_response.json()["user"]["id"]
    
    # Mentor 1 creates a course
    course_data = {
        "title": "Python for Data Science",
        "description": "Learn Python for data analysis and machine learning"
    }
    
    mentor1_headers = {"Authorization": f"Bearer {mentor1_token}"}
    mentor2_headers = {"Authorization": f"Bearer {mentor2_token}"}
    
    create_response = session.post(f"{BACKEND_URL}/courses", json=course_data, headers=mentor1_headers)
    
    if create_response.status_code != 200:
        print("❌ Failed to create course")
        return False
    
    course = create_response.json()
    course_id = course["id"]
    
    print("✅ Mentor 1 created course")
    
    # Mentor 1 can access their own pending course
    mentor1_access = session.get(f"{BACKEND_URL}/courses/{course_id}", headers=mentor1_headers)
    if mentor1_access.status_code != 200:
        print("❌ Mentor 1 should access their own course")
        return False
    
    print("✅ Mentor 1 can access their own pending course")
    
    # Mentor 2 cannot access Mentor 1's pending course
    mentor2_access = session.get(f"{BACKEND_URL}/courses/{course_id}", headers=mentor2_headers)
    if mentor2_access.status_code != 403:
        print(f"❌ Expected 403 for Mentor 2 accessing Mentor 1's course, got: {mentor2_access.status_code}")
        return False
    
    print("✅ Mentor 2 correctly denied access to Mentor 1's pending course")
    
    # Mentor 2 cannot update Mentor 1's course
    update_data = {"title": "Updated Title"}
    mentor2_update = session.put(f"{BACKEND_URL}/courses/{course_id}", json=update_data, headers=mentor2_headers)
    if mentor2_update.status_code != 403:
        print(f"❌ Expected 403 for Mentor 2 updating Mentor 1's course, got: {mentor2_update.status_code}")
        return False
    
    print("✅ Mentor 2 correctly denied update access to Mentor 1's course")
    
    # Mentor 2 cannot access Mentor 1's courses via mentor endpoint
    mentor2_view_mentor1 = session.get(f"{BACKEND_URL}/courses/mentor/{mentor1_id}", headers=mentor2_headers)
    if mentor2_view_mentor1.status_code != 403:
        print(f"❌ Expected 403 for Mentor 2 viewing Mentor 1's courses, got: {mentor2_view_mentor1.status_code}")
        return False
    
    print("✅ Mentor 2 correctly denied access to view Mentor 1's courses")
    
    # Mentor 1 can view their own courses via mentor endpoint
    mentor1_view_own = session.get(f"{BACKEND_URL}/courses/mentor/{mentor1_id}", headers=mentor1_headers)
    if mentor1_view_own.status_code != 200:
        print("❌ Mentor 1 should access their own courses")
        return False
    
    own_courses = mentor1_view_own.json()
    if len(own_courses) == 0:
        print("❌ Mentor 1 should see their own course")
        return False
    
    print("✅ Mentor 1 can view their own courses")
    
    print("\n🎉 Mentor access control test PASSED!")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 ADDITIONAL COURSE MANAGEMENT TESTS")
    print("=" * 60)
    
    results = []
    results.append(test_approval_workflow())
    results.append(test_mentor_access_control())
    
    print("\n" + "=" * 60)
    print("📊 ADDITIONAL TESTS SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All additional tests passed!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} additional test(s) failed.")
        sys.exit(1)