from django.core.management.base import BaseCommand
from student_management_app.models import CustomUser, Staffs


class Command(BaseCommand):
    help = 'Fix missing Staffs records for CustomUser objects with user_type="2"'

    def handle(self, *args, **options):
        self.stdout.write("Checking for staff users without Staffs records...")
        
        # Get all staff users (user_type='2')
        staff_users = CustomUser.objects.filter(user_type='2')
        self.stdout.write(f"Found {staff_users.count()} staff users")
        
        fixed_count = 0
        
        for user in staff_users:
            try:
                # Try to get the corresponding Staffs record
                staff_record = Staffs.objects.get(admin=user)
                self.stdout.write(f"✓ Staff record exists for user: {user.username}")
            except Staffs.DoesNotExist:
                # Create missing Staffs record
                self.stdout.write(f"✗ Missing Staffs record for user: {user.username}")
                staff_record = Staffs.objects.create(admin=user, address="")
                self.stdout.write(
                    self.style.SUCCESS(f"✓ Created Staffs record for user: {user.username}")
                )
                fixed_count += 1
        
        self.stdout.write(f"\nSummary:")
        self.stdout.write(f"Total staff users: {staff_users.count()}")
        self.stdout.write(f"Fixed missing records: {fixed_count}")
        
        if fixed_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f"\n✓ Fixed {fixed_count} missing Staffs records!")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("\n✓ All staff users have corresponding Staffs records!")
            )
