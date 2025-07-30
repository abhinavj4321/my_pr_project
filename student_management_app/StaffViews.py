from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.utils.timezone import now
import json
import random
import string
import datetime
import uuid
import qrcode
import os
from io import BytesIO
from django.core.files.base import ContentFile

# Try to import pandas, but handle the case where it's not installed
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except (ImportError, AttributeError):
    PANDAS_AVAILABLE = False

from student_management_app.models import (
    CustomUser, Staffs, Courses, Subjects, Students,
    SessionYearModel, Attendance, AttendanceReport, StudentResult
)
from .models import AttendanceQRCode
from .utils import get_client_ip
from .utils import export_attendance_to_excel

def staff_generate_qr(request):
    print(f"QR Generation request: {request.method}")  # Debug
    if request.method == "POST":
        print(f"POST data: {request.POST}")  # Debug
        subject_id = request.POST.get('subject')
        session_year_id = request.POST.get('session_year')
        expiry_minutes = request.POST.get('expiry_time', 30)
        teacher_latitude = request.POST.get('latitude')
        teacher_longitude = request.POST.get('longitude')
        allowed_radius = request.POST.get('radius', 10)

        # Network verification parameters
        require_same_network = request.POST.get('require_same_network', False)
        teacher_ip = request.POST.get('teacher_ip')
        teacher_ssid = request.POST.get('teacher_ssid')

        print(f"Parsed data - Subject: {subject_id}, Session: {session_year_id}, Expiry: {expiry_minutes}")  # Debug

        # Ensure required fields are present
        if not subject_id or not session_year_id:
            print("Missing required fields!")  # Debug
            return JsonResponse({"status": "error", "message": "Subject and session year are required."}, status=400)

        try:
            subject = Subjects.objects.get(id=subject_id)
            session_year = SessionYearModel.objects.get(id=session_year_id)

            unique_token = str(uuid.uuid4())

            # Create a URL that includes the token for direct scanning
            # This URL will redirect to the login page if user is not logged in
            qr_data = f"{request.build_absolute_uri('/scan-attendance/')}?token={unique_token}"

            qr = qrcode.make(qr_data)
            qr_io = BytesIO()
            qr.save(qr_io, format="PNG")

            # Create QR code instance with basic fields first
            qr_code_instance = AttendanceQRCode(
                subject=subject,
                session_year=session_year,
                expiry_time=now() + datetime.timedelta(minutes=int(expiry_minutes)),
                is_active=True,
                token=unique_token,
                teacher_latitude=float(teacher_latitude) if teacher_latitude else None,
                teacher_longitude=float(teacher_longitude) if teacher_longitude else None,
                allowed_radius=float(allowed_radius)
            )

            # Add network verification fields if they exist in the model
            try:
                qr_code_instance.require_same_network = bool(require_same_network)
                qr_code_instance.teacher_ip_address = teacher_ip
                qr_code_instance.teacher_network_ssid = teacher_ssid
            except AttributeError:
                # Network fields don't exist yet, skip them
                pass
            qr_code_instance.qr_code_image.save(f"qr_{subject.id}_{session_year.id}.png", ContentFile(qr_io.getvalue()), save=True)

            # Get the full URL to the QR code image
            qr_code_url = qr_code_instance.qr_code_image.url

            # Also include the base64 encoded image data for direct sharing
            import base64
            qr_io.seek(0)  # Reset the pointer to the beginning of the BytesIO object
            qr_base64 = base64.b64encode(qr_io.getvalue()).decode('utf-8')
            qr_data_url = f"data:image/png;base64,{qr_base64}"

            return JsonResponse({
                "status": "success",
                "qr_code_url": qr_code_instance.qr_code_image.url,
                "qr_data_url": qr_data_url,  # Include the base64 data URL
                "expiry_time": qr_code_instance.expiry_time.strftime("%Y-%m-%d %H:%M:%S"),
            })

        except Subjects.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Invalid subject ID."}, status=400)
        except SessionYearModel.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Invalid session year ID."}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=400)



def staff_home(request):
    # Get the Staff instance linked to the logged-in user
    staff_instance = Staffs.objects.get(admin=request.user)

    # Fetch only subjects assigned to this staff
    subjects = Subjects.objects.filter(staff_id=staff_instance)
    course_id_list = []
    for subject in subjects:
        course = Courses.objects.get(id=subject.course_id.id)
        course_id_list.append(course.id)

    final_course = []
    for course_id in course_id_list:
        if course_id not in final_course:
            final_course.append(course_id)

    students_count = Students.objects.filter(course_id__in=final_course).count()
    subject_count = subjects.count()

    attendance_count = Attendance.objects.filter(subject_id__in=subjects).count()

    subject_list = []
    attendance_list = []
    for subject in subjects:
        attendance_count1 = Attendance.objects.filter(subject_id=subject.id).count()
        subject_list.append(subject.subject_name)
        attendance_list.append(attendance_count1)

    # Get students and their attendance data
    students_attendance = Students.objects.filter(course_id__in=final_course)
    student_list = []
    student_list_attendance_present = []
    student_list_attendance_absent = []

    # Enhance students_attendance with attendance data
    for student in students_attendance:
        attendance_present_count = AttendanceReport.objects.filter(status=True, student_id=student.id).count()
        attendance_absent_count = AttendanceReport.objects.filter(status=False, student_id=student.id).count()
        # Add attendance data as attributes to student objects
        student.attendance_present = attendance_present_count
        student.attendance_absent = attendance_absent_count

        # Still maintain the lists for charts or other uses
        student_list.append(student.admin.first_name+" "+ student.admin.last_name)
        student_list_attendance_present.append(attendance_present_count)
        student_list_attendance_absent.append(attendance_absent_count)

    context={
        "students_count": students_count,
        "attendance_count": attendance_count,
        "subject_count": subject_count,
        "subject_list": subject_list,
        "attendance_list": attendance_list,
        "student_list": student_list,
        "attendance_present_list": student_list_attendance_present,
        "attendance_absent_list": student_list_attendance_absent,
        "students_attendance": students_attendance,
        "subjects": subjects
    }
    return render(request, "staff_template/staff_home_template.html", context)



from django.contrib.auth.decorators import login_required

@login_required
def staff_take_attendance(request):
    try:
        # Get the Staff instance linked to the logged-in user
        staff_instance = Staffs.objects.get(admin=request.user)

        # Fetch only subjects assigned to this staff
        subjects = Subjects.objects.filter(staff_id=staff_instance)

        # Check if a specific subject was requested
        selected_subject_id = request.GET.get('subject')
        selected_subject = None

        if selected_subject_id:
            try:
                selected_subject = subjects.get(id=selected_subject_id)
            except Subjects.DoesNotExist:
                # If the subject doesn't exist or doesn't belong to this staff
                pass

    except Staffs.DoesNotExist:
        # Handle case where staff entry is missing
        subjects = []
        selected_subject = None

    # Fetch all session years
    session_years = SessionYearModel.objects.all()

    context = {
        "subjects": subjects,
        "session_years": session_years,
        "selected_subject": selected_subject
    }
    return render(request, "staff_template/take_attendance_template.html", context)


@csrf_exempt
def get_students(request):
    subject_id = request.POST.get("subject")
    session_year = request.POST.get("session_year")

    # Validate input parameters
    if not subject_id or not session_year:
        return JsonResponse({"error": "Subject ID and Session Year are required"}, status=400)

    try:
        # Get the Staff instance linked to the logged-in user
        staff_instance = Staffs.objects.get(admin=request.user)

        # Verify the subject belongs to this staff
        subject_model = Subjects.objects.get(id=subject_id, staff_id=staff_instance)
        session_model = SessionYearModel.objects.get(id=session_year)

        # Get students for this course and session
        students = Students.objects.filter(course_id=subject_model.course_id, session_year_id=session_model)

        if students.count() == 0:
            # No students found for this course and session
            return JsonResponse(json.dumps({"message": "No students found for this course and session"}),
                               content_type="application/json", safe=False)

    except Staffs.DoesNotExist:
        # Staff not found
        return JsonResponse(json.dumps({"error": "Staff not found"}), content_type="application/json", safe=False)
    except Subjects.DoesNotExist:
        # If subject doesn't exist or doesn't belong to this staff
        return JsonResponse(json.dumps({"error": "Subject not found or not assigned to you"}),
                           content_type="application/json", safe=False)
    except SessionYearModel.DoesNotExist:
        # Session year not found
        return JsonResponse(json.dumps({"error": "Session year not found"}), content_type="application/json", safe=False)
    except Exception as e:
        # Other errors
        return JsonResponse(json.dumps({"error": str(e)}), content_type="application/json", safe=False)

    list_data = []

    for student in students:
        data_small={"id":student.admin.id, "name":student.admin.first_name+" "+student.admin.last_name}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)




@csrf_exempt
def save_attendance_data(request):

    student_ids = request.POST.get("student_ids")
    subject_id = request.POST.get("subject_id")
    attendance_date = request.POST.get("attendance_date")
    session_year_id = request.POST.get("session_year_id")

    subject_model = Subjects.objects.get(id=subject_id)
    session_year_model = SessionYearModel.objects.get(id=session_year_id)

    json_student = json.loads(student_ids)

    try:
        attendance = Attendance(subject_id=subject_model, attendance_date=attendance_date, session_year_id=session_year_model)
        attendance.save()

        for stud in json_student:
            student = Students.objects.get(admin=stud['id'])
            # For manually taken attendance, set location_verified to True if the student is present
            location_verified = stud['status'] == 1  # True if present, False if absent
            attendance_report = AttendanceReport(
                student_id=student,
                attendance_id=attendance,
                status=stud['status'],
                location_verified=location_verified  # Set location verification status
            )
            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("Error")




def staff_update_attendance(request):
    # Get the Staff instance linked to the logged-in user
    staff_instance = Staffs.objects.get(admin=request.user)

    # Fetch only subjects assigned to this staff
    subjects = Subjects.objects.filter(staff_id=staff_instance)
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "staff_template/update_attendance_template.html", context)

def staff_view_attendance(request):
    """View for staff to view attendance records"""
    # Get the Staff instance linked to the logged-in user
    staff_instance = Staffs.objects.get(admin=request.user)

    # Fetch only subjects assigned to this staff
    subjects = Subjects.objects.filter(staff_id=staff_instance)

    # Fetch all session years
    session_years = SessionYearModel.objects.all()

    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "staff_template/view_attendance_template.html", context)

@csrf_exempt
def get_attendance_dates(request):
    # Get parameters from request
    subject_id = request.POST.get("subject")
    session_year = request.POST.get("session_year_id")

    try:
        # Get the Staff instance linked to the logged-in user
        staff_instance = Staffs.objects.get(admin=request.user)

        # Verify the subject belongs to this staff
        subject_model = Subjects.objects.get(id=subject_id, staff_id=staff_instance)
        session_model = SessionYearModel.objects.get(id=session_year)

        # Get attendance records for this subject and session
        attendance = Attendance.objects.filter(subject_id=subject_model, session_year_id=session_model)
    except Subjects.DoesNotExist:
        # If subject doesn't exist or doesn't belong to this staff
        return JsonResponse(json.dumps([]), content_type="application/json", safe=False)

    list_data = []

    for attendance_single in attendance:
        data_small={"id":attendance_single.id, "attendance_date":str(attendance_single.attendance_date), "session_year_id":attendance_single.session_year_id.id}
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def get_attendance_student(request):
    attendance_date = request.POST.get('attendance_date')
    attendance = Attendance.objects.get(id=attendance_date)

    attendance_data = AttendanceReport.objects.filter(attendance_id=attendance)
    list_data = []

    for student in attendance_data:
        # Include location_verified field in the response
        data_small={
            "id": student.student_id.admin.id,
            "name": student.student_id.admin.first_name+" "+student.student_id.admin.last_name,
            "status": student.status,
            "location_verified": student.location_verified
        }
        list_data.append(data_small)

    return JsonResponse(json.dumps(list_data), content_type="application/json", safe=False)


@csrf_exempt
def update_attendance_data(request):
    student_ids = request.POST.get("student_ids")

    attendance_date = request.POST.get("attendance_date")
    attendance = Attendance.objects.get(id=attendance_date)

    json_student = json.loads(student_ids)

    try:

        for stud in json_student:
            student = Students.objects.get(admin=stud['id'])

            attendance_report = AttendanceReport.objects.get(student_id=student, attendance_id=attendance)
            attendance_report.status = stud['status']

            # Update location_verified field based on status
            # If status is changing to present, set location_verified to True for manual attendance
            if stud['status'] == 1 and not attendance_report.status:
                attendance_report.location_verified = True
            # If status is changing to absent, set location_verified to False
            elif stud['status'] == 0:
                attendance_report.location_verified = False
            # Otherwise, keep the existing location_verified value

            attendance_report.save()
        return HttpResponse("OK")
    except:
        return HttpResponse("Error")


@csrf_exempt
def delete_attendance(request):
    """Delete an attendance record and all associated attendance reports"""
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method."}, status=400)

    attendance_id = request.POST.get("attendance_id")
    if not attendance_id:
        return JsonResponse({"status": "error", "message": "Attendance ID is required."}, status=400)

    try:
        # Get the attendance record
        attendance = Attendance.objects.get(id=attendance_id)

        # Check if the subject belongs to the staff
        if attendance.subject_id.staff_id.admin.id != request.user.id:
            return JsonResponse({"status": "error", "message": "You don't have permission to delete this attendance record."}, status=403)

        # Delete all attendance reports associated with this attendance
        AttendanceReport.objects.filter(attendance_id=attendance).delete()

        # Delete the attendance record
        attendance.delete()

        return JsonResponse({"status": "success", "message": "Attendance record deleted successfully."})

    except Attendance.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Attendance record not found."}, status=404)

    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error deleting attendance record: {str(e)}"}, status=500)


def staff_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    staff = Staffs.objects.get(admin=user)

    context={
        "user": user,
        "staff": staff
    }
    return render(request, 'staff_template/staff_profile.html', context)


def staff_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('staff_profile')
    else:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        address = request.POST.get('address')

        try:
            customuser = CustomUser.objects.get(id=request.user.id)
            customuser.first_name = first_name
            customuser.last_name = last_name
            if password != None and password != "":
                customuser.set_password(password)
            customuser.save()

            staff = Staffs.objects.get(admin=customuser.id)
            staff.address = address
            staff.save()

            messages.success(request, "Profile Updated Successfully")
            return redirect('staff_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('staff_profile')


def staff_apply_leave(request):
    """View for staff to apply for leave"""
    staff = Staffs.objects.get(admin=request.user.id)
    context = {
        "staff": staff
    }
    return render(request, "staff_template/staff_apply_leave.html", context)


def staff_feedback(request):
    """View for staff to provide feedback"""
    staff = Staffs.objects.get(admin=request.user.id)
    context = {
        "staff": staff
    }
    return render(request, "staff_template/staff_feedback.html", context)


def staff_add_result(request):
    # Get the Staff instance linked to the logged-in user
    staff_instance = Staffs.objects.get(admin=request.user)

    # Fetch only subjects assigned to this staff
    subjects = Subjects.objects.filter(staff_id=staff_instance)
    session_years = SessionYearModel.objects.all()
    context = {
        "subjects": subjects,
        "session_years": session_years,
    }
    return render(request, "staff_template/add_result_template.html", context)


def staff_add_result_save(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('staff_add_result')
    else:
        student_admin_id = request.POST.get('student_list')
        assignment_marks = request.POST.get('assignment_marks')
        exam_marks = request.POST.get('exam_marks')
        subject_id = request.POST.get('subject')

        student_obj = Students.objects.get(admin=student_admin_id)
        subject_obj = Subjects.objects.get(id=subject_id)

        try:
            # Check if Students Result Already Exists or not
            check_exist = StudentResult.objects.filter(subject_id=subject_obj, student_id=student_obj).exists()
            if check_exist:
                result = StudentResult.objects.get(subject_id=subject_obj, student_id=student_obj)
                result.subject_assignment_marks = assignment_marks
                result.subject_exam_marks = exam_marks
                result.save()
                messages.success(request, "Result Updated Successfully!")
                return redirect('staff_add_result')
            else:
                result = StudentResult(student_id=student_obj, subject_id=subject_obj, subject_exam_marks=exam_marks, subject_assignment_marks=assignment_marks)
                result.save()
                messages.success(request, "Result Added Successfully!")
                return redirect('staff_add_result')
        except:
            messages.error(request, "Failed to Add Result!")
            return redirect('staff_add_result')

def staff_export_attendance(request):
    """View for exporting staff's attendance data"""
    # Get the staff ID from the user
    staff = Staffs.objects.get(admin=request.user.id)

    # Get subjects taught by this staff
    subjects = Subjects.objects.filter(staff_id=staff)

    # Get all session years
    session_years = SessionYearModel.objects.all()

    context = {
        "subjects": subjects,
        "session_years": session_years
    }
    return render(request, "staff_template/staff_export_attendance.html", context)


def staff_import_attendance(request):
    """View for staff to import attendance from Excel"""
    # Get the staff ID from the user
    staff = Staffs.objects.get(admin=request.user.id)

    # Get subjects taught by this staff
    subjects = Subjects.objects.filter(staff_id=staff)

    # Get all session years
    session_years = SessionYearModel.objects.all()

    # Get today's date for default value
    today_date = datetime.datetime.now().strftime('%Y-%m-%d')

    context = {
        "subjects": subjects,
        "session_years": session_years,
        "today_date": today_date,
        "pandas_available": PANDAS_AVAILABLE
    }
    return render(request, "staff_template/staff_import_attendance.html", context)


@csrf_exempt
def staff_import_attendance_data(request):
    """Process Excel file upload and import attendance data"""
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Invalid request method."})

    # Check if pandas is available
    if not PANDAS_AVAILABLE:
        return JsonResponse({
            "status": "error",
            "message": "The pandas library is not installed. Please install it using 'pip install pandas openpyxl' to use this feature."
        })

    try:
        subject_id = request.POST.get('subject')
        session_year_id = request.POST.get('session_year')
        attendance_date = request.POST.get('attendance_date')
        excel_file = request.FILES.get('excel_file')

        # Validate inputs
        if not subject_id or not session_year_id or not attendance_date or not excel_file:
            return JsonResponse({"status": "error", "message": "All fields are required."})

        # Check file extension
        if not excel_file.name.endswith(('.xls', '.xlsx')):
            return JsonResponse({"status": "error", "message": "Only Excel files (.xls, .xlsx) are allowed."})

        # Get subject and session year objects
        subject = Subjects.objects.get(id=subject_id)
        session_year = SessionYearModel.objects.get(id=session_year_id)

        # Check if subject belongs to the staff
        if subject.staff_id.admin.id != request.user.id:
            return JsonResponse({"status": "error", "message": "You don't have permission to import attendance for this subject."})

        # Parse Excel file
        df = pd.read_excel(excel_file)

        # Print column names for debugging
        print(f"Excel columns: {df.columns.tolist()}")

        # Normalize column names (strip whitespace, convert to lowercase)
        df.columns = [str(col).strip().lower() for col in df.columns]

        # Check if required columns exist (case-insensitive)
        required_columns = ['student id', 'student name', 'status']
        for col in required_columns:
            if col not in df.columns:
                return JsonResponse({"status": "error", "message": f"Column '{col}' is missing in the Excel file. Available columns: {', '.join(df.columns.tolist())}. Please use the export function to get the correct format."})

        # Check if Date column exists - it's optional but useful
        has_date_column = 'date' in df.columns

        # Create or get attendance record
        attendance, _ = Attendance.objects.get_or_create(
            subject_id=subject,
            attendance_date=attendance_date,
            session_year_id=session_year
        )

        # Process each row in the Excel file
        success_count = 0
        error_count = 0
        processed_dates = set()

        for _, row in df.iterrows():
            try:
                # Get student ID from the Excel file (using lowercase column name)
                student_id_raw = row['student id']
                # Convert to string and strip any whitespace
                student_id = str(student_id_raw).strip()

                # Get date from the row if available, otherwise use the provided date
                row_date = None
                if has_date_column and not pd.isna(row['date']):
                    try:
                        # Try to parse the date from the Excel file
                        row_date = pd.to_datetime(row['date']).date()
                        processed_dates.add(row_date)
                    except:
                        # If date parsing fails, use the provided date
                        row_date = None

                # Use the date from the form if no date in the row or date parsing failed
                current_date = row_date or datetime.datetime.strptime(attendance_date, '%Y-%m-%d').date()

                # Handle different status formats (boolean, string, or numeric)
                status_value = row['status']
                if isinstance(status_value, str):
                    # Handle string values like 'Present' or 'Absent'
                    status = status_value.lower() in ['present', 'yes', 'true', '1']
                elif isinstance(status_value, (int, float)):
                    # Handle numeric values (1 = Present, 0 = Absent)
                    status = bool(status_value)
                else:
                    # Default to boolean conversion
                    status = bool(status_value)

                # Get student object - try to find by admin_id (which is the CustomUser ID)
                try:
                    student = Students.objects.get(admin_id=student_id)
                except Students.DoesNotExist:
                    # If not found by admin_id, try to find by username
                    try:
                        custom_user = CustomUser.objects.get(username=str(student_id))
                        student = Students.objects.get(admin=custom_user)
                    except (CustomUser.DoesNotExist, Students.DoesNotExist):
                        raise Exception(f"Student with ID '{student_id}' not found")

                # Get or create attendance record for this date
                attendance, _ = Attendance.objects.get_or_create(
                    subject_id=subject,
                    attendance_date=current_date,
                    session_year_id=session_year
                )

                # Create or update attendance report
                _, _ = AttendanceReport.objects.update_or_create(
                    student_id=student,
                    attendance_id=attendance,
                    defaults={'status': status}
                )

                success_count += 1
            except Exception as e:
                print(f"Error processing row: {e}")
                error_count += 1
                continue

        # Create a more detailed success message
        dates_message = ""
        if processed_dates:
            date_list = sorted(processed_dates)
            if len(date_list) == 1:
                dates_message = f" for {date_list[0]}"
            elif len(date_list) > 1:
                dates_message = f" for {len(date_list)} dates from {date_list[0]} to {date_list[-1]}"

        return JsonResponse({
            "status": "success",
            "message": f"Attendance imported successfully{dates_message}. {success_count} records processed, {error_count} errors."
        })

    except Subjects.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Subject not found."})
    except SessionYearModel.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Session year not found."})
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"Error importing attendance: {str(e)}"})

@csrf_exempt
def staff_export_attendance_data(request):
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed", status=405)

    subject_id = request.POST.get('subject')
    session_year_id = request.POST.get('session_year')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    if not subject_id or not session_year_id or not start_date or not end_date:
        return JsonResponse({'status': 'error', 'message': 'Missing required fields'})

    try:
        subject = Subjects.objects.get(id=subject_id)
        session_year = SessionYearModel.objects.get(id=session_year_id)

        # Convert string dates to datetime objects
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        # Get attendance records for the specified period
        attendances = Attendance.objects.filter(
            subject_id=subject,
            session_year_id=session_year,
            attendance_date__range=(start_date, end_date)
        )

        if not attendances:
            # Check if there are any attendance records for this subject at all
            any_attendance = Attendance.objects.filter(subject_id=subject).exists()

            if any_attendance:
                return JsonResponse({
                    'status': 'error',
                    'message': f'No attendance records found between {start_date} and {end_date} for {subject.subject_name}. Please try a different date range.'
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': f'No attendance records found for {subject.subject_name}. Please take attendance first before exporting.'
                })

        # Get all attendance reports for these attendances
        attendance_reports = AttendanceReport.objects.filter(attendance_id__in=attendances)

        if not attendance_reports:
            return JsonResponse({'status': 'error', 'message': 'No attendance data found for the selected criteria'})

        # Generate Excel file
        date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        excel_file = export_attendance_to_excel(
            attendance_reports,
            subject_name=subject.subject_name,
            date_range=date_range
        )

        # Prepare filename
        filename = f"attendance_{subject.subject_name}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.xlsx"

        # Read the file content instead of keeping it open
        with open(excel_file, 'rb') as f:
            file_content = f.read()

        # Create the response with the content
        response = HttpResponse(
            file_content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        # Set headers to force download
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(file_content)

        # Close and delete the file explicitly before returning the response
        try:
            os.unlink(excel_file)
        except Exception as file_error:
            # If we can't delete now, schedule it for later
            import atexit
            atexit.register(lambda file_path=excel_file: os.unlink(file_path) if os.path.exists(file_path) else None)
            print(f"Warning: Could not delete temp file immediately: {str(file_error)}")

        return response

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return JsonResponse({'status': 'error', 'message': str(e)})


@csrf_exempt
def get_network_info(request):
    """Get teacher's network information for network verification"""
    if request.method == 'GET':
        try:
            # Get teacher's IP address
            teacher_ip = get_client_ip(request)

            return JsonResponse({
                'status': 'success',
                'ip_address': teacher_ip
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Error getting network info: {str(e)}'
            })

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
