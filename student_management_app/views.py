from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse

from student_management_app.EmailBackEnd import EmailBackEnd


def home(request):
    return render(request, 'index.html')


def loginPage(request):
    return render(request, 'login.html')



def doLogin(request):
    if request.method != "POST":
        return HttpResponse("<h2>Method Not Allowed</h2>")
    else:
        user = EmailBackEnd.authenticate(request, username=request.POST.get('email'), password=request.POST.get('password'))
        if user != None:
            login(request, user)
            user_type = user.user_type

            # Check if there's an attendance token in the session
            attendance_token = request.session.get('attendance_token')

            if user_type == '1':
                return redirect('admin_home')

            elif user_type == '2':
                return redirect('staff_home')

            elif user_type == '3':
                # If student has an attendance token, redirect to scan QR page
                if attendance_token:
                    # Keep the token in session, it will be processed by student_scan_qr
                    return redirect('student_scan_qr')
                else:
                    return redirect('student_home')
            else:
                messages.error(request, "Invalid Login!")
                return redirect('login')
        else:
            messages.error(request, "Invalid Login Credentials!")
            return redirect('login')



def get_user_details(request):
    if request.user != None:
        return HttpResponse("User: "+request.user.email+" User Type: "+request.user.user_type)
    else:
        return HttpResponse("Please Login First")



def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')


def scan_attendance_qr(request):
    """
    Handle QR code scanning from external sources.
    This function accepts a token parameter and:
    1. If user is logged in as a student, processes the attendance
    2. If user is not logged in, saves the token in session and redirects to login
    """
    token = request.GET.get('token')

    if not token:
        messages.error(request, "Invalid QR code. No token provided.")
        return redirect('login')

    # If user is already logged in and is a student
    if request.user.is_authenticated and request.user.user_type == '3':
        # Redirect to student scan processing with the token in session
        request.session['attendance_token'] = token
        return redirect('student_scan_qr')

    # If user is not logged in, save token in session and redirect to login
    request.session['attendance_token'] = token
    messages.info(request, "Please log in to mark your attendance.")
    return redirect('login')


