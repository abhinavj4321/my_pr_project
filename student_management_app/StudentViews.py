from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, FileResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage, default_storage
from django.urls import reverse
from django.utils.timezone import now
from django.core.cache import cache
import datetime
import os
# OpenCV is optional for deployment
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("OpenCV not available - QR scanning will use alternative methods")

import numpy as np
import json
import tempfile
from PIL import Image

from django.views.decorators.csrf import csrf_exempt
from student_management_app.models import (
    CustomUser, Staffs, Courses, Subjects, Students,
    Attendance, AttendanceReport, StudentResult, SessionYearModel
)
from .utils import get_client_ip, verify_network_connectivity
from .models import AttendanceQRCode
from .utils import is_within_radius, export_attendance_to_excel

def student_home(request):
    student_obj = Students.objects.get(admin=request.user.id)
    total_attendance = AttendanceReport.objects.filter(student_id=student_obj).count()
    attendance_present = AttendanceReport.objects.filter(student_id=student_obj, status=True).count()
    attendance_absent = AttendanceReport.objects.filter(student_id=student_obj, status=False).count()

    course_obj = Courses.objects.get(id=student_obj.course_id.id)
    total_subjects = Subjects.objects.filter(course_id=course_obj).count()

    subject_name = []
    data_present = []
    data_absent = []
    subject_data = Subjects.objects.filter(course_id=student_obj.course_id)
    for subject in subject_data:
        attendance = Attendance.objects.filter(subject_id=subject.id)
        attendance_present_count = AttendanceReport.objects.filter(attendance_id__in=attendance, status=True, student_id=student_obj.id).count()
        attendance_absent_count = AttendanceReport.objects.filter(attendance_id__in=attendance, status=False, student_id=student_obj.id).count()
        subject_name.append(subject.subject_name)
        data_present.append(attendance_present_count)
        data_absent.append(attendance_absent_count)

    context={
        "total_attendance": total_attendance,
        "attendance_present": attendance_present,
        "attendance_absent": attendance_absent,
        "total_subjects": total_subjects,
        "subject_name": subject_name,
        "data_present": data_present,
        "data_absent": data_absent
    }
    return render(request, "student_template/student_home_template.html", context)

def decode_qr_code(image_path):
    """ Decodes QR Code using OpenCV (if available) """
    if not OPENCV_AVAILABLE:
        return None

    try:
        img = cv2.imread(image_path)
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(img)
        return data if data else None
    except Exception as e:
        print(f"OpenCV QR decode error: {e}")
        return None

@csrf_exempt
def student_upload_qr(request):
    if request.method == 'POST':
        try:
            # Check if QR code image is provided
            if 'qr_image' not in request.FILES:
                return JsonResponse({'status': 'error', 'message': 'No QR code image provided'})

            # Get the uploaded QR code image
            qr_image = request.FILES['qr_image']

            # Get student's location data
            latitude = request.POST.get('latitude')
            longitude = request.POST.get('longitude')

            # Open and process the QR code image
            try:
                import datetime
                from django.utils.timezone import now
                import tempfile
                import os

                token = None

                # Try pyzbar first
                try:
                    from pyzbar.pyzbar import decode
                    from PIL import Image

                    # Open the image using PIL
                    img = Image.open(qr_image)

                    # Decode the QR code
                    decoded_objects = decode(img)

                    if decoded_objects:
                        # Get the QR code data (token)
                        token = decoded_objects[0].data.decode('utf-8')
                except Exception as pyzbar_error:
                    print(f"Pyzbar failed: {pyzbar_error}")

                # If pyzbar failed, try OpenCV as fallback (if available)
                if not token and OPENCV_AVAILABLE:
                    try:
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                            for chunk in qr_image.chunks():
                                temp_file.write(chunk)
                            temp_file_path = temp_file.name

                        # Use OpenCV to decode
                        token = decode_qr_code(temp_file_path)

                        # Clean up temp file
                        os.unlink(temp_file_path)
                    except Exception as opencv_error:
                        print(f"OpenCV failed: {opencv_error}")

                if not token:
                    return JsonResponse({'status': 'error', 'message': 'No QR code found in the image or unable to decode'})

                # Find the corresponding QR code record in the database
                try:
                    qr_code = AttendanceQRCode.objects.filter(
                        token=token,
                        is_active=True,
                        expiry_time__gte=now()
                    ).first()

                    if not qr_code:
                        return JsonResponse({'status': 'error', 'message': 'QR code has expired or is invalid'})

                    # Get the student object
                    student = Students.objects.get(admin=request.user.id)

                    # Check if attendance already marked
                    attendance_exists = Attendance.objects.filter(
                        subject_id=qr_code.subject,
                        session_year_id=qr_code.session_year,
                        attendance_date=datetime.date.today()
                    ).exists()

                    if attendance_exists:
                        attendance = Attendance.objects.get(
                            subject_id=qr_code.subject,
                            session_year_id=qr_code.session_year,
                            attendance_date=datetime.date.today()
                        )

                        # Check if student already marked attendance
                        if AttendanceReport.objects.filter(student_id=student, attendance_id=attendance).exists():
                            return JsonResponse({'status': 'error', 'message': 'You have already marked attendance for this subject today'})
                    else:
                        # Create new attendance record
                        attendance = Attendance(
                            subject_id=qr_code.subject,
                            attendance_date=datetime.date.today(),
                            session_year_id=qr_code.session_year
                        )
                        attendance.save()

                    # Verify location if teacher's location is available
                    location_verified = False
                    if qr_code.teacher_latitude and qr_code.teacher_longitude and latitude and longitude:
                        # Convert to float
                        student_lat = float(latitude)
                        student_lon = float(longitude)
                        teacher_lat = float(qr_code.teacher_latitude)
                        teacher_lon = float(qr_code.teacher_longitude)
                        allowed_radius = float(qr_code.allowed_radius)

                        # Debug logging for upload QR
                        print(f"Upload QR Location verification debug:")
                        print(f"Student location: {student_lat}, {student_lon}")
                        print(f"Teacher location: {teacher_lat}, {teacher_lon}")
                        print(f"Allowed radius: {allowed_radius}")

                        # Check if student is within allowed radius
                        from .utils import is_within_radius

                        verification_result = is_within_radius(
                            student_lat, student_lon,
                            teacher_lat, teacher_lon,
                            allowed_radius
                        )

                        print(f"Upload QR Verification result: {verification_result}")

                        # Extract the boolean value for location verification
                        location_verified = bool(verification_result['is_within'])

                        if not location_verified:
                            return JsonResponse({
                                'status': 'error',
                                'message': f'You are not within the allowed radius for attendance. You are {verification_result["distance"]:.2f} meters away from the teacher, but the allowed radius is {verification_result["original_radius"]:.2f} meters.',
                                'debug_info': {
                                    'student_location': f'{student_lat:.6f}, {student_lon:.6f}',
                                    'teacher_location': f'{teacher_lat:.6f}, {teacher_lon:.6f}',
                                    'distance_calculated': round(verification_result["distance"], 2)
                                }
                            })

                    # Network verification removed - only location-based verification is used

                    # Create attendance report with proper data types
                    # Create a verification details dictionary if we have location data
                    verification_details = None
                    if location_verified is not None and 'verification_result' in locals():
                        verification_details = {
                            'distance': float(verification_result['distance']),
                            'allowed_radius': float(verification_result['original_radius']),
                            'effective_radius': float(verification_result['effective_radius']),
                            'error_margin': float(verification_result['error_margin']),
                            'is_reliable': bool(verification_result['is_reliable'])
                        }

                    # Network verification removed - no longer needed

                    # Create attendance report with basic fields
                    attendance_report = AttendanceReport(
                        student_id=student,
                        attendance_id=attendance,
                        status=True,
                        student_latitude=float(latitude) if latitude else None,
                        student_longitude=float(longitude) if longitude else None,
                        location_verified=bool(location_verified),
                        verification_details=verification_details
                    )

                    # Network verification removed - no longer needed
                    attendance_report.save()

                    return JsonResponse({
                        'status': 'success',
                        'message': 'Attendance marked successfully'
                    })

                except Exception as qr_error:
                    return JsonResponse({'status': 'error', 'message': f'Error validating QR code: {str(qr_error)}'})

            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'Error processing QR code: {str(e)}'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error: {str(e)}'})

    return render(request, 'student_template/student_upload_qr.html')


def student_view_attendance(request):
    student = Students.objects.get(admin=request.user.id)
    course = student.course_id
    subjects = Subjects.objects.filter(course_id=course)
    return render(request, "student_template/student_view_attendance.html", {"subjects": subjects})


def student_view_attendance_post(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method")
        return redirect('student_view_attendance')

    subject_id = request.POST.get('subject')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    if not subject_id or not start_date or not end_date:
        messages.error(request, "Please select a subject and date range.")
        return redirect("student_view_attendance")

    try:
        start_date_parse = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_parse = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        subject_obj = Subjects.objects.get(id=subject_id)
        user_obj = CustomUser.objects.get(id=request.user.id)
        stud_obj = Students.objects.get(admin=user_obj)

        attendance = Attendance.objects.filter(
            attendance_date__range=(start_date_parse, end_date_parse),
            subject_id=subject_obj
        )
        attendance_reports = AttendanceReport.objects.filter(
            attendance_id__in=attendance, student_id=stud_obj
        )

        return render(request, 'student_template/student_attendance_data.html', {
            "subject_obj": subject_obj,
            "attendance_reports": attendance_reports
        })

    except Subjects.DoesNotExist:
        messages.error(request, "Invalid subject selected.")
        return redirect("student_view_attendance")

    except Exception as e:
        messages.error(request, f"Error processing request: {str(e)}")
        return redirect("student_view_attendance")



def student_profile(request):
    user = CustomUser.objects.get(id=request.user.id)
    student = Students.objects.get(admin=user)

    context={
        "user": user,
        "student": student
    }
    return render(request, 'student_template/student_profile.html', context)


def student_profile_update(request):
    if request.method != "POST":
        messages.error(request, "Invalid Method!")
        return redirect('student_profile')
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

            student = Students.objects.get(admin=customuser.id)
            student.address = address
            student.save()

            messages.success(request, "Profile Updated Successfully")
            return redirect('student_profile')
        except:
            messages.error(request, "Failed to Update Profile")
            return redirect('student_profile')


def student_view_result(request):
    student = Students.objects.get(admin=request.user.id)
    student_result = StudentResult.objects.filter(student_id=student.id)
    context = {
        "student_result": student_result,
    }
    return render(request, "student_template/student_view_result.html", context)


def student_scan_qr(request):
    """View for camera-based QR code scanning"""
    # Check if there's a token in the session from external QR code scan
    attendance_token = request.session.get('attendance_token')

    context = {}
    if attendance_token:
        context['attendance_token'] = attendance_token
        # Clear the token from session to prevent reuse
        del request.session['attendance_token']

    return render(request, 'student_template/student_scan_qr.html', context)


@csrf_exempt
@login_required
def student_process_qr_scan(request):
    """Process QR code data from camera scan"""
    if request.method == 'POST':
        try:
            # Check if user is a student
            if request.user.user_type != '3':
                return JsonResponse({'status': 'error', 'message': 'Access denied. Students only.'})

            # Get the QR code data from the request
            data = json.loads(request.body)
            token = data.get('token')
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            student_ssid = data.get('network_ssid')  # Network SSID from student

            if not token:
                return JsonResponse({'status': 'error', 'message': 'No QR code data provided'})

            # Find the corresponding QR code record in the database
            try:
                qr_code = AttendanceQRCode.objects.filter(
                    token=token,
                    is_active=True,
                    expiry_time__gte=now()
                ).first()

                if not qr_code:
                    return JsonResponse({'status': 'error', 'message': 'QR code has expired or is invalid'})

                # Get the student object
                student = Students.objects.get(admin=request.user.id)

                # Check if attendance already marked
                attendance_exists = Attendance.objects.filter(
                    subject_id=qr_code.subject,
                    session_year_id=qr_code.session_year,
                    attendance_date=datetime.date.today()
                ).exists()

                if attendance_exists:
                    attendance = Attendance.objects.get(
                        subject_id=qr_code.subject,
                        session_year_id=qr_code.session_year,
                        attendance_date=datetime.date.today()
                    )

                    # Check if student already marked attendance
                    if AttendanceReport.objects.filter(student_id=student, attendance_id=attendance).exists():
                        return JsonResponse({'status': 'error', 'message': 'You have already marked attendance for this subject today'})
                else:
                    # Create new attendance record
                    attendance = Attendance(
                        subject_id=qr_code.subject,
                        attendance_date=datetime.date.today(),
                        session_year_id=qr_code.session_year
                    )
                    attendance.save()

                # Verify location if teacher's location is available
                location_verified = False
                location_details = {}

                if qr_code.teacher_latitude and qr_code.teacher_longitude and latitude and longitude:
                    # Convert to float
                    student_lat = float(latitude)
                    student_lon = float(longitude)
                    teacher_lat = float(qr_code.teacher_latitude)
                    teacher_lon = float(qr_code.teacher_longitude)
                    allowed_radius = float(qr_code.allowed_radius)

                    # Debug logging
                    print(f"Location verification debug:")
                    print(f"Student location: {student_lat}, {student_lon}")
                    print(f"Teacher location: {teacher_lat}, {teacher_lon}")
                    print(f"Allowed radius: {allowed_radius}")

                    # Get student location accuracy if available
                    student_accuracy = data.get('accuracy', None)
                    print(f"Student accuracy: {student_accuracy}")

                    # Check if student is within allowed radius with enhanced verification
                    verification_result = is_within_radius(
                        student_lat, student_lon,
                        teacher_lat, teacher_lon,
                        allowed_radius,
                        student_accuracy
                    )

                    print(f"Verification result: {verification_result}")

                    # Store verification details for the response
                    location_details = {
                        'distance': round(verification_result['distance'], 2),
                        'allowed_radius': round(verification_result['original_radius'], 2),
                        'effective_radius': round(verification_result['effective_radius'], 2),
                        'error_margin': round(verification_result['error_margin'], 2),
                        'is_reliable': bool(verification_result['is_reliable'])  # Ensure it's a proper boolean
                    }

                    print(f"Location details: {location_details}")

                    # Check if coordinates are suspiciously identical
                    if student_lat == teacher_lat and student_lon == teacher_lon:
                        print("WARNING: Student and teacher coordinates are identical!")

                    # Check if student is within radius
                    location_verified = verification_result['is_within']
                    print(f"Location verified: {location_verified}")

                    if not location_verified:
                        # Provide more detailed error message with distance information
                        return JsonResponse({
                            'status': 'error',
                            'message': f'You are not within the allowed radius for attendance. You are {location_details["distance"]} meters away from the teacher, but the allowed radius is {location_details["allowed_radius"]} meters.',
                            'location_details': location_details,
                            'debug_info': {
                                'student_location': f'{student_lat:.6f}, {student_lon:.6f}',
                                'teacher_location': f'{teacher_lat:.6f}, {teacher_lon:.6f}',
                                'distance_calculated': location_details["distance"]
                            }
                        })
                else:
                    # If teacher's location is not set, location verification is not required
                    if qr_code.teacher_latitude and qr_code.teacher_longitude:
                        # Teacher has location but student doesn't - require location
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Location data is required to mark attendance. Please enable location services and try again.'
                        })
                    else:
                        # No location verification required
                        location_verified = True  # Allow attendance without location verification

                # Network verification using cached data
                network_verified = False
                network_verification_details = None
                student_ip = get_client_ip(request)

                # Get network information from cache
                cache_key = f"qr_network_{token}"
                network_info = cache.get(cache_key)

                print(f"Network verification debug:")
                print(f"- Cache key: {cache_key}")
                print(f"- Network info from cache: {network_info}")
                print(f"- Student IP: {student_ip}")

                if network_info and network_info.get('require_network_verification'):
                    teacher_ip = network_info.get('teacher_ip')
                    teacher_ssid = network_info.get('teacher_ssid')

                    # Perform network verification
                    network_verification_result = verify_network_connectivity(
                        student_ip=student_ip,
                        teacher_ip=teacher_ip,
                        student_ssid=student_ssid,
                        teacher_ssid=teacher_ssid
                    )

                    network_verified = network_verification_result['is_same_network']
                    network_verification_details = {
                        'student_ip': student_ip,
                        'teacher_ip': teacher_ip,
                        'student_ssid': student_ssid,
                        'teacher_ssid': teacher_ssid,
                        'ip_match': network_verification_result['ip_match'],
                        'ssid_match': network_verification_result['ssid_match'],
                        'verification_method': network_verification_result['verification_method']
                    }

                    if not network_verified:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Network verification failed. You must be connected to the same network as your teacher.',
                            'network_details': network_verification_details
                        })
                else:
                    # Network verification not required or no network info available
                    print("Network verification skipped - not required or no network info available")
                    network_verified = True

                # Create attendance report with enhanced location details
                # Convert location_details to a proper JSON-serializable format
                json_location_details = None
                if location_details:
                    # Ensure all values are proper JSON types (bool, float, int, str, list, dict)
                    json_location_details = {
                        'distance': float(location_details['distance']),
                        'allowed_radius': float(location_details['allowed_radius']),
                        'effective_radius': float(location_details['effective_radius']),
                        'error_margin': float(location_details['error_margin']),
                        'is_reliable': bool(location_details['is_reliable'])
                    }

                # Create attendance report with available fields
                # Store network verification details in the existing verification_details field
                combined_verification_details = json_location_details or {}
                if network_verification_details:
                    combined_verification_details['network'] = network_verification_details
                    combined_verification_details['network_verified'] = network_verified

                attendance_report = AttendanceReport(
                    student_id=student,
                    attendance_id=attendance,
                    status=True,
                    student_latitude=student_lat if latitude else None,
                    student_longitude=student_lon if longitude else None,
                    student_accuracy=float(student_accuracy) if student_accuracy else None,
                    location_verified=bool(location_verified),
                    verification_details=combined_verification_details
                )

                attendance_report.save()

                # Deactivate QR Code after successful attendance marking
                # qr_code.is_active = False
                # qr_code.save()

                return JsonResponse({
                    'status': 'success',
                    'message': 'Attendance marked successfully',
                    'subject': qr_code.subject.subject_name,
                    'location_verified': location_verified,
                    'location_details': location_details if location_details else None,
                    'network_verified': network_verified,
                    'network_details': network_verification_details if network_verification_details else None
                })

            except AttendanceQRCode.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Invalid QR code'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error: {str(e)}'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def student_export_attendance(request):
    """View for exporting student's attendance data"""
    student = Students.objects.get(admin=request.user.id)
    course = student.course_id
    subjects = Subjects.objects.filter(course_id=course)
    context = {
        "subjects": subjects
    }
    return render(request, "student_template/student_export_attendance.html", context)


@csrf_exempt
def student_export_attendance_data(request):
    """Export student's attendance data to Excel"""
    if request.method != 'POST':
        return HttpResponse("Method Not Allowed", status=405)

    subject_id = request.POST.get('subject')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')

    if not start_date or not end_date:
        return JsonResponse({'status': 'error', 'message': 'Date range is required'})

    try:
        # Get the student object
        student = Students.objects.get(admin=request.user.id)

        # Convert string dates to datetime objects
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

        # Filter attendance records
        if subject_id and subject_id != '0':  # If a specific subject is selected
            subject = Subjects.objects.get(id=subject_id)
            attendances = Attendance.objects.filter(
                subject_id=subject,
                attendance_date__range=(start_date, end_date)
            )
            subject_name = subject.subject_name
        else:  # All subjects
            course = student.course_id
            subjects = Subjects.objects.filter(course_id=course)
            attendances = Attendance.objects.filter(
                subject_id__in=subjects,
                attendance_date__range=(start_date, end_date)
            )
            subject_name = "All Subjects"

        # Get attendance reports for this student
        attendance_reports = AttendanceReport.objects.filter(
            attendance_id__in=attendances,
            student_id=student
        )

        if not attendance_reports:
            return JsonResponse({'status': 'error', 'message': 'No attendance records found for the selected criteria'})

        # Generate Excel file
        date_range = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        excel_file = export_attendance_to_excel(
            attendance_reports,
            subject_name=subject_name,
            date_range=date_range,
            for_student=True
        )

        # Prepare filename
        student_name = f"{student.admin.first_name}_{student.admin.last_name}"
        filename = f"attendance_{student_name}_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.xlsx"

        # Read the file content instead of keeping it open
        with open(excel_file, 'rb') as f:
            file_content = f.read()

        # Create the response with the content
        response = HttpResponse(
            file_content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        # Set the Content-Disposition header
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
