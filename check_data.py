#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')

# Setup Django
django.setup()

from student_management_app.models import *

def check_data():
    print("=== Current Database Status ===")
    
    print(f"\nCourses ({Courses.objects.count()}):")
    for course in Courses.objects.all():
        print(f"  - ID: {course.id}, Name: {course.course_name}")
    
    print(f"\nSession Years ({SessionYearModel.objects.count()}):")
    for session in SessionYearModel.objects.all():
        print(f"  - ID: {session.id}, Start: {session.session_start_year}, End: {session.session_end_year}")
    
    print(f"\nStaff ({Staffs.objects.count()}):")
    for staff in Staffs.objects.all():
        print(f"  - ID: {staff.id}, User: {staff.admin.username}")
    
    print(f"\nSubjects ({Subjects.objects.count()}):")
    for subject in Subjects.objects.all():
        print(f"  - ID: {subject.id}, Name: {subject.subject_name}, Course: {subject.course_id.course_name}, Staff: {subject.staff_id.admin.username}")
    
    print(f"\nCustom Users ({CustomUser.objects.count()}):")
    for user in CustomUser.objects.all():
        print(f"  - ID: {user.id}, Username: {user.username}, Type: {user.user_type}")

if __name__ == "__main__":
    check_data()
