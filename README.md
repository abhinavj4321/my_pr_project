# QR Code Attendance System

This is a Student Attendance System with QR Code functionality developed for Educational Purpose using Python (Django).

If you like this project, please add a STAR ⭐️ to this project 👆

## Features of this Project

### A. Admin Users Can

1. See Overall Summary Charts of Students Performance, Staffs Performances, Courses, Subjects, etc.
2. Manage Staffs (Add, Update and Delete)
3. Manage Students (Add, Update and Delete)
4. Manage Course (Add, Update and Delete)
5. Manage Subjects (Add, Update and Delete)
6. Manage Sessions (Add, Update and Delete)
7. View Student Attendance
8. Assign teachers to courses and subjects

### B. Staff/Teachers Can

1. See the Overall Summary Charts related to their students, their subjects, etc.
2. Take/Update Students Attendance using QR codes
3. Generate QR codes for attendance with location verification
4. Add/Update Result
5. Export attendance data to Excel
6. Import attendance data from Excel
7. Share QR codes via WhatsApp

### C. Students Can

1. See the Overall Summary Charts related to their attendance, their subjects, etc.
2. View Attendance
3. View Result
4. Scan QR codes for attendance with location verification
5. Export their attendance records to Excel

## New Features Added

1. QR Code Generation and Scanning for Attendance
2. Location Verification between Students and Teachers
3. WhatsApp Sharing of QR Codes
4. Excel Import/Export Functionality
5. Calendar View for Attendance
6. Manual Attendance Management

## How to Install and Run this project?

### Pre-Requisites:

1. Install Git Version Control
   [ https://git-scm.com/ ]

2. Install Python Latest Version
   [ https://www.python.org/downloads/ ]

3. Install Pip (Package Manager)
   [ https://pip.pypa.io/en/stable/installing/ ]

### Installation

**1. Create a Folder where you want to save the project**

**2. Create a Virtual Environment and Activate**

Install Virtual Environment First

```
$  pip install virtualenv
```

Create Virtual Environment

For Windows

```
$  python -m venv venv
```

For Mac

```
$  python3 -m venv venv
```

Activate Virtual Environment

For Windows

```
$  venv\scripts\activate
```

For Mac

```
$  source venv/bin/activate
```

**3. Clone this project**

```
$  git clone https://github.com/anuj452005/Qr-code-attendece.git
```

Then, Enter the project

```
$  cd Qr-code-attendece
```

**4. Install Requirements from 'requirements.txt'**

```python
$  pip install -r requirements.txt
```

**5. Add the hosts**

- Go to settings.py file
- Then, On allowed hosts, Add ['*'].

```python
ALLOWED_HOSTS = ['*']
```

**6. Now Run Server**

Command for PC:

```python
$ python manage.py runserver
```

Command for Mac:

```python
$ python3 manage.py runserver
```

**7. Login Credentials**

Create Super User (HOD)

```
$  python manage.py createsuperuser
```

Then Add Email, Username and Password

**or Use Default Credentials**

_For HOD /SuperAdmin_
Email: admin@gmail.com
Password: admin

_For Staff_
Email: staff@gmail.com
Password: staff

_For Student_
Email: student@gmail.com
Password: student

## License

This project is licensed under the MIT License.
