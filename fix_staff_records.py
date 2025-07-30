#!/usr/bin/env python
"""
Script to fix missing Staffs records for CustomUser objects with user_type='2'
Run this script using: python manage.py shell < fix_staff_records.py
"""

from student_management_app.models import CustomUser, Staffs

def fix_staff_records():
    """
    Check for CustomUser objects with user_type='2' that don't have corresponding Staffs records
    and create them.
    """
    print("Checking for staff users without Staffs records...")
    
    # Get all staff users (user_type='2')
    staff_users = CustomUser.objects.filter(user_type='2')
    print(f"Found {staff_users.count()} staff users")
    
    fixed_count = 0
    
    for user in staff_users:
        try:
            # Try to get the corresponding Staffs record
            staff_record = Staffs.objects.get(admin=user)
            print(f"✓ Staff record exists for user: {user.username}")
        except Staffs.DoesNotExist:
            # Create missing Staffs record
            print(f"✗ Missing Staffs record for user: {user.username}")
            staff_record = Staffs.objects.create(admin=user, address="")
            print(f"✓ Created Staffs record for user: {user.username}")
            fixed_count += 1
    
    print(f"\nSummary:")
    print(f"Total staff users: {staff_users.count()}")
    print(f"Fixed missing records: {fixed_count}")
    
    if fixed_count > 0:
        print(f"\n✓ Fixed {fixed_count} missing Staffs records!")
    else:
        print("\n✓ All staff users have corresponding Staffs records!")

# Run the function
fix_staff_records()
