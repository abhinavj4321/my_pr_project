import os
import django
import datetime

# Set up Django environment
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
django.setup()

# Now we can import Django models
from student_management_app.models import SessionYearModel, Courses

# Create a default session year if none exists
def create_default_session_year():
    session_years = SessionYearModel.objects.all()
    if not session_years.exists():
        print("Creating default session year...")
        today = datetime.date.today()
        next_year = today.replace(year=today.year + 1)
        session_year = SessionYearModel(
            session_start_year=today,
            session_end_year=next_year
        )
        session_year.save()
        print(f"Default session year created: {today} to {next_year}")
    else:
        print(f"Session years already exist: {len(session_years)} found")
        for session in session_years:
            print(f"  - {session.session_start_year} to {session.session_end_year}")

# Create a default course if none exists
def create_default_course():
    courses = Courses.objects.all()
    if not courses.exists():
        print("Creating default course...")
        course = Courses(
            course_name="Default Course"
        )
        course.save()
        print(f"Default course created: {course.course_name}")
    else:
        print(f"Courses already exist: {len(courses)} found")
        for course in courses:
            print(f"  - {course.course_name}")

if __name__ == "__main__":
    print("Setting up default data...")
    create_default_session_year()
    create_default_course()
    print("Setup complete.")