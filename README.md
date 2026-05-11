# QR-Based Student Attendance System

A comprehensive Django-based Student Management System featuring automated QR code attendance, geolocation verification, and dedicated portals for Admins, Staff, and Students.

## 🚀 Key Features

### User Roles & Portals
- **Admin/HOD Portal:** Manage staff, students, courses, subjects, and sessions. View overall attendance and results.
- **Staff Portal:** Add/Manage results, view student lists, and generate dynamic QR codes for secure attendance tracking.
- **Student Portal:** View results, track personal attendance, and securely check in to classes via QR scanning.

### 📍 Advanced QR Attendance System
- Dynamic QR code generation for each class session.
- **Geolocation Verification:** Validates that the student is physically within an allowed radius (meters) of the teacher.
- **Time-restricted Tokens:** QR codes expire automatically after a specified time frame.
- **Fraud Prevention:** Checks location accuracy to prevent fake network/location spoofing.

### 📚 Academic Management
- Manage Academic Sessions (Start & End Years)
- Course & Subject allocations

## 🛠️ Technology Stack

- **Backend:** Python 3.13, Django 4.2
- **Database:** PostgreSQL (Production via psycopg), SQLite (Local)
- **Frontend:** Bootstrap 4, AdminLTE (templates), Chart.js for visualization
- **Geodata & Vision:** Geopy (Location distance calculation), OpenCV/Pillow, `qrcode`
- **Deployment:** Ready for Render (includes `render.yaml`, `Procfile`, Gunicorn, Whitenoise for static files)

## ⚙️ Installation & Setup (Local Development)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd my_pr_project
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create Superuser (Admin)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the Development Server**
   ```bash
   python manage.py runserver
   ```
   *Access the app at `http://127.0.0.1:8000`*

## 🌍 Live Demo & Production Deployment (Render)

**Live Demo:** [https://my-pr-project.onrender.com](https://my-pr-project.onrender.com)

This project is pre-configured for deployment on Render.
- Uses `dj-database-url` for the database connection.
- Built-in `build.sh` script to automate dependencies installing, collecting static files, and running migrations during the build phase.
- `render.yaml` for infrastructure as code.

## 📜 Project Structure Highlights
- `/student_management_app/`: Main Django app housing Views (HOD, Staff, Student), Models, and API logic.
- `/student_management_system/`: Core Django configurations & settings.
- `/static/`: CSS, JS, Fonts, and Vendor libraries (AdminLTE context).

## 📄 License
This project is open-source and free to use for academic purposes.
