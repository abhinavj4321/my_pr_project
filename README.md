# Prescripto - Doctor Appointment Booking System

## Live Demos
- **Frontend (User Portal):** [https://doctor-appointment-o08ak5twc-abhinav-jaiswals-projects-ad8a93c8.vercel.app/](https://doctor-appointment-o08ak5twc-abhinav-jaiswals-projects-ad8a93c8.vercel.app/)
- **Admin Portal:** [https://doctor-appointment-zxdl-d11atk65z.vercel.app/](https://doctor-appointment-zxdl-d11atk65z.vercel.app/)
- **Backend API:** [https://doctor-appointment-9328.onrender.com](https://doctor-appointment-9328.onrender.com)

## Overview
A comprehensive full-stack MERN application that allows patients to browse doctors by specialty and book appointments seamlessly. It also includes an Admin panel for system management and a Doctor panel for managing upcoming appointments.

## Features
- **User Portal:** 
  - Browse doctors by specialty.
  - Book, view, and cancel appointments.
  - User authentication and profile management.
  - Payment gateway integration (Stripe & Razorpay).
- **Admin Portal:**
  - Add and manage doctors, including photo uploads.
  - View all system appointments and overall dashboard metrics.
  - Secure admin authentication.
- **Doctor Portal:**
  - View booked appointments exclusively assigned to them.
  - Mark appointments as completed or cancelled.
  - Manage dashboard earnings and professional profile.

## Tech Stack
- **Frontend & Admin:** React.js (Vite), Tailwind CSS, Context API
- **Backend:** Node.js, Express.js
- **Database:** MongoDB Atlas
- **Media Storage:** Cloudinary
- **Authentication:** JSON Web Tokens (JWT)
- **Payments:** Stripe SDK, Razorpay API

## Project Structure
This is a monorepo containing three micro-applications:
- `/backend`: Node.js/Express framework handling APIs, database connections, and business logic.
- `/frontend`: The main client-facing web application for users/patients.
- `/admin`: The dashboard application for administrators and system doctors.

---

## Local Setup Instructions

### 1. Prerequisites
- **Node.js** installed on your machine
- **MongoDB Atlas** account for DB URI
- **Cloudinary** account for image assets
- **Stripe / Razorpay** accounts (for checking out)

### 2. Installation
Clone the repository and install the NPM packages in all three directories:

```bash
# Install backend dependencies
cd backend
npm install

# Install frontend dependencies
cd ../frontend
npm install

# Install admin dependencies
cd ../admin
npm install
```

### 3. Environment Variables
Create a `.env` file inside each of the respective applications with the following placeholders:

#### `backend/.env`
```env
PORT=4000
MONGODB_URI=------ MongoDB URI here ------
CLOUDINARY_NAME=------ Cloudinary Name here ------
CLOUDINARY_API_KEY=------ Cloudinary API key here ------
CLOUDINARY_SECRET_KEY=------ Cloudinary Secret key here ------
JWT_SECRET=supersecretstring
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=securepassword
CURRENCY=INR
RAZORPAY_KEY_ID=------ Razorpay Key Id here ------
RAZORPAY_KEY_SECRET=------ Razorpay Key Secret here ------
STRIPE_SECRET_KEY=------ Stripe Secret Key here ------
```

#### `frontend/.env`
```env
VITE_BACKEND_URL=http://localhost:4000
VITE_RAZORPAY_KEY_ID=------ Razorpay Key Id here ------
```

#### `admin/.env`
```env
VITE_BACKEND_URL=http://localhost:4000
VITE_CURRENCY=₹
```

### 4. Running the Application
You will need to run all three servers simultaneously. Open three separate terminal windows:

**Terminal 1 (Backend):**
```bash
cd backend
npm run server
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

**Terminal 3 (Admin):**
```bash
cd admin
npm run dev
```

---

## Cloud Deployment Guide

This project is optimized for deployment via **Render** and **Vercel**.

1. **Backend (Render):**
   - Create a New Web Service.
   - Set **Root Directory** to `backend`.
   - Set Build Command to `npm install` and Start Command to `npm start`.
   - Add all backend environment variables.
2. **Frontend (Vercel):**
   - Import the repository and set **Root Directory** to `frontend`.
   - Add `VITE_BACKEND_URL` pointing to the Render backend URL.
3. **Admin Panel (Vercel):**
   - Import the repository again and set **Root Directory** to `admin`.
   - Add `VITE_BACKEND_URL` and `VITE_CURRENCY` variables.
