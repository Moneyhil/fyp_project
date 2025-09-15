Blood Donation Management System
==========================================

Project ID: 21-KS-BSIT-11
Project Name: Blood Donation Management System
Session: 2021-2025
Submitted by: Manahil Saeed (Reg No: 2021-KS-482, PU Roll No: 068420)
Supervisor: Hasan Raza

Project Overview

The Blood Donation Management System is a comprehensive mobile application designed to bridge the gap between blood donors and recipients. The system facilitates efficient communication, request management, and tracking of blood donation activities.

Key Objectives:
- Connect blood donors with recipients efficiently
- Streamline the blood donation request process
- Provide real-time tracking and notifications
- Ensure secure user authentication and data management
- Enable emergency blood request handling

System Architecture
Frontend (React Native with Expo)
- Framework: React Native 0.81.4 with Expo SDK 54
- Navigation: Expo Router 6.0.4
- State Management: React Hooks and AsyncStorage
- UI Components: React Native Paper, Custom Components
- Form Handling: Formik with Yup validation

Backend (Django REST Framework)
- Framework: Django 4.2.7 with Django REST Framework
- Authentication: JWT (Simple JWT)
- Database:  MySQL (configurable)
- Email Service: SMTP with Gmail integration
- API: RESTful API with comprehensive endpoints

Features
 User Management
- User registration with email verification
- OTP-based authentication system
- Profile management for donors and recipients
- Role-based access control
- Account activation/deactivation

Donor Features
- Donor profile creation and management
- Availability status updates
- Blood group and location information
- Donation history tracking
- Email notifications for requests

Recipient Features
- Search donors by blood type and location
- Create blood donation requests
- Track request status
- Direct communication with donors
- Emergency request handling

Admin Features
- User management and monitoring
- System analytics and reporting
- Content moderation
- System configuration

Communication System
- Email notifications
- Request status updates
- Confirmation emails with HTML templates

Technology Stack
Frontend Dependencies
- React Native 0.81.4
- Expo SDK 54.0.7
- Expo Router 6.0.4
- React Navigation 7.x
- Axios 1.11.0
- Formik 2.4.6
- Yup 1.7.0
- React Native Paper 5.14.5
- AsyncStorage 2.2.0

Backend Dependencies
- Django 4.2.7
- Django REST Framework
- Django REST Framework Simple JWT
- Django CORS Headers
- Python Dotenv


Installation Guide
Prerequisites
- Node.js (LTS version 18.x or higher)
- Python 3.10+
- MySQL 8.0+
- Expo go

Backend Setup

1-Create virtual environment:
python -m venv venv

2-Activate virtual environment:
- Windows: venv\Scripts\activate

3.Install dependencies:
pip install django djangorestframework
pip install djangorestframework-simplejwt
pip install django-cors-headers
pip install python-dotenv
pip install mysqlclient

4.Configure environment variables:
Create .env file in backend/djangobackend/:

SECRET_KEY=your-secret-key-here
DB_ENGINE=django.db.backends.mysql
DB_NAME=blood_donation_db
DB_USER=your-db-username
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=3306
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

5.Setup database:
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

6.Run development server:
python manage.py runserver 0.0.0.0:8000

Frontend Setup
1.Navigate to frontend directory:
  cd fyp_project/frontend1

2. Install dependencies:
  npm install

3. Start Expo development server:
  npx expo start

Configuration
Backend Configuration

Database Settings (settings.py):
Configure MySQL connection
Set up email SMTP settings
Configure CORS origins
JWT token settings

Email Configuration:
Gmail SMTP integration
HTML email templates
Automated notifications
Frontend Configuration

API Configuration:
Update API base URL in utils/api.js
Configure authentication headers
Set up request/response interceptors


Database Schema
Core Models
User Model:

Custom user model extending AbstractUser
Fields: name, email, contact_number, blood_group, city, address
Authentication and profile management

Profile Model:

Extended user information
Donor/recipient specific data
Availability status


MonthlyDonationTracker Model:

Monthly donation statistics
Goal tracking
Performance metrics

Blood Donation Management System
==========================================

Project ID: 21-KS-BSIT-11
Project Name: Blood Donation Management System
Session: 2021-2025
Submitted by: Manahil Saeed (Reg No: 2021-KS-482, PU Roll No: 068420)
Supervisor: Hasan Raza


Project Overview

The Blood Donation Management System is a comprehensive mobile application designed to bridge the gap between blood donors and recipients. The system facilitates efficient communication, request management, and tracking of blood donation activities.

Key Objectives:
- Connect blood donors with recipients efficiently
- Streamline the blood donation request process
- Provide real-time tracking and notifications
- Ensure secure user authentication and data management
- Enable emergency blood request handling

System Architecture
Frontend (React Native with Expo)
- Framework: React Native 0.81.4 with Expo SDK 54
- Navigation: Expo Router 6.0.4
- State Management: React Hooks and AsyncStorage
- UI Components: React Native Paper, Custom Components
- Form Handling: Formik with Yup validation

Backend (Django REST Framework)
- Framework: Django 4.2.7 with Django REST Framework
- Authentication: JWT (Simple JWT)
- Database:  MySQL (configurable)
- Email Service: SMTP with Gmail integration
- API: RESTful API with comprehensive endpoints

Features
 User Management
- User registration with email verification
- OTP-based authentication system
- Profile management for donors and recipients
- Role-based access control
- Account activation/deactivation

Donor Features
- Donor profile creation and management
- Availability status updates
- Blood group and location information
- Donation history tracking
- Email notifications for requests

Recipient Features
- Search donors by blood type and location
- Create blood donation requests
- Track request status
- Direct communication with donors
- Emergency request handling

Admin Features
- User management and monitoring
- System analytics and reporting
- Content moderation
- System configuration

Communication System
- Email notifications
- Request status updates
- Confirmation emails with HTML templates

Technology Stack
Frontend Dependencies
- React Native 0.81.4
- Expo SDK 54.0.7
- Expo Router 6.0.4
- React Navigation 7.x
- Axios 1.11.0
- Formik 2.4.6
- Yup 1.7.0
- React Native Paper 5.14.5
- AsyncStorage 2.2.0

Backend Dependencies
- Django 4.2.7
- Django REST Framework
- Django REST Framework Simple JWT
- Django CORS Headers
- Python Dotenv


Installation Guide
Prerequisites
- Node.js (LTS version 18.x or higher)
- Python 3.10+
- MySQL 8.0+
- Expo go

Backend Setup

1-Create virtual environment:
python -m venv venv

2-Activate virtual environment:
- Windows: venv\Scripts\activate

3.Install dependencies:
pip install django djangorestframework
pip install djangorestframework-simplejwt
pip install django-cors-headers
pip install python-dotenv
pip install mysqlclient

4.Configure environment variables:
Create .env file in backend/djangobackend/:

SECRET_KEY=your-secret-key-here
DB_ENGINE=django.db.backends.mysql
DB_NAME=blood_donation_db
DB_USER=your-db-username
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=3306
EMAIL_HOST_USER=your-gmail@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

5.Setup database:
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

6.Run development server:
python manage.py runserver 0.0.0.0:8000

Frontend Setup
1.Navigate to frontend directory:
  cd fyp_project/frontend1

2. Install dependencies:
  npm install

3. Start Expo development server:
  npx expo start

Configuration
Backend Configuration

Database Settings (settings.py):
Configure MySQL connection
Set up email SMTP settings
Configure CORS origins
JWT token settings

Email Configuration:
Gmail SMTP integration
HTML email templates
Automated notifications
Frontend Configuration

API Configuration:
Update API base URL in utils/api.js
Configure authentication headers
Set up request/response interceptors


Database Schema
Core Models
User Model:

Custom user model extending AbstractUser
Fields: name, email, contact_number, blood_group, city, address
Authentication and profile management

Profile Model:

Extended user information
Donor/recipient specific data
Availability status


MonthlyDonationTracker Model:

Monthly donation statistics
Goal tracking
Performance metrics


Git Repository

Repository URL: https://github.com/Moneyhil/fyp_project.git




