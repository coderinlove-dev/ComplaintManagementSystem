# Complaint Management System

A web-based Complaint Management System built with Flask (Python), MySQL, and frontend technologies.  
This project allows students to register complaints, admins to manage them, and staff to resolve assigned complaints.


## 🚀 Features

- User registration and login (Student, Staff, Admin roles)
- JWT-based authentication
- Admin can approve/reject staff accounts
- Admin can assign complaints to staff
- Staff can update complaint statuses
- Students can raise complaints and track progress
- Secure password hashing (bcrypt)

## 📂 Project Structure

ComplaintManagementSystem/
│── backend/ # Flask backend
│ ├── app.py # Main Flask app
│ ├── config/ # Config & schema
│ │ └── complaint_db_schema.sql
│ ├── routes/ # Routes (admin, staff, student)
│ ├── models/ # DB helpers
│ └── ...
│── frontend/ # HTML, CSS, JS
│── README.md

## 🛠️ Prerequisites
Make sure you have installed:
- Python 3.8+
- MySQL Server 8.0+
- Node.js (if using frontend build tools)

## ⚙️ Backend Setup

1. Clone the repository
```bash
git clone https://github.com/your-username/complaint-management-system.git
cd ComplaintManagementSystem/backend

2. Create a virtual environment and activate
python -m venv venv
venv\Scripts\activate   # On Windows

3. Install dependencies
pip install -r requirements.txt


🗄️ Database Setup

1. Create the database
CREATE DATABASE complaint_db;

2. Load schema from file
mysql -u root -p complaint_db < backend/config/complaint_db_schema.sql
(This will create all required tables (users, complaints, roles, etc.))

3. Create the first admin user
INSERT INTO users (name, email, password, role_id, is_approved, staff_status)
VALUES (
    'Admin',
    'admin@cms.com',
    '$2b$10$NcdROGuDJ7FC.nPy//.3D.JBLUVncZPg1ztPbOdRgY8PZgoGMxYCq', -- bcrypt hash for "admin123"
    1,
    TRUE,
    'Authorized'
);

✅ Default Admin Credentials: 1.Email : admin@cms.com , 2.Password: admin123


▶️ Running the Backend
cd backend
python app.py

🖥️ Frontend
1.Open the frontend/ folder and start a local server
(or open index.html directly in a browser).
2.Make sure the backend is running first.

🔑 Admin Login
Go to the login page and use:  1.Email : admin@cms.com , 2.Password: admin123


✅ Done!
Now the system is ready for:
- Students to register & raise complaints
- Admin to manage complaints & staff
- Staff to resolve assigned complaints






















