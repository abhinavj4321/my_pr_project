from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from student_management_app.models import (
    CustomUser, Staffs, Students, Courses, Subjects,
    SessionYearModel, Attendance, AttendanceReport,
    StudentResult, AttendanceQRCode, AdminHOD
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Reset database - Remove all data except admin users'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This command will delete ALL data except admin users!\n'
                    'This includes:\n'
                    '- All staff members\n'
                    '- All students\n'
                    '- All courses and subjects\n'
                    '- All attendance records\n'
                    '- All session years\n'
                    '- All QR codes\n'
                    '- All student results\n'
                    '\nTo proceed, run: python manage.py reset_database --confirm'
                )
            )
            return

        self.stdout.write('Starting database reset...')

        try:
            # Delete all non-admin users first (this will cascade to related models)
            # Keep only admin users (user_type = 1)
            non_admin_users = CustomUser.objects.exclude(user_type=1)
            deleted_users = non_admin_users.delete()[0]
            self.stdout.write(f'Deleted {deleted_users} user accounts (students and staff)')

            # Delete remaining orphaned records
            deleted_count = AttendanceReport.objects.all().delete()[0]
            self.stdout.write(f'Deleted {deleted_count} attendance reports')

            deleted_count = Attendance.objects.all().delete()[0]
            self.stdout.write(f'Deleted {deleted_count} attendance records')

            deleted_count = AttendanceQRCode.objects.all().delete()[0]
            self.stdout.write(f'Deleted {deleted_count} QR codes')

            deleted_count = StudentResult.objects.all().delete()[0]
            self.stdout.write(f'Deleted {deleted_count} student results')

            deleted_count = Subjects.objects.all().delete()[0]
            self.stdout.write(f'Deleted {deleted_count} subjects')

            deleted_count = Courses.objects.all().delete()[0]
            self.stdout.write(f'Deleted {deleted_count} courses')

            deleted_count = SessionYearModel.objects.all().delete()[0]
            self.stdout.write(f'Deleted {deleted_count} session years')

            self.stdout.write(
                self.style.SUCCESS(
                    '\nDatabase reset completed successfully!\n'
                    'Only admin users have been preserved.\n'
                    'You can now add new courses, staff, and students.'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during database reset: {str(e)}')
            )
            raise
