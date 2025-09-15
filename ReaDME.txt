Blood Donation App
==================

Project ID: 21-KS-BSIT-11
Project Name: Blood Donation App
Session: 2021-2025
Submitted by: Manahil Saeed (Reg No: 2021-KS-482, PU Roll No: 068420)
Supervisor: Hasan Raza

------------------------------------------------------------
📌 Project Description
------------------------------------------------------------
The Blood Donation App is designed to bridge the gap between blood donors and recipients by 
providing an efficient platform for communication. The app allows donors to register and 
update their availability, while recipients can search for donors by blood type and city. 

Features include:
- User registration and authentication with OTP verification
- Donor/Recipient profile management
- Search donors by blood type and location
- Direct call functionality between donor and recipient
- Admin panel to manage users, block accounts, and monitor activity

------------------------------------------------------------
⚙️ Installation & Configuration Instructions
------------------------------------------------------------

1. Prerequisites:
   - Python 3.10+
   - Node.js (LTS version)
   - install npm 
   - MySQL Database
   - Git (optional, for version control)

2. Backend Setup (Django + DRF + MySQL):
   - Clone or extract the project folder.
   - Navigate to the `backend/` directory.
   - Create a virtual environment:
     > python -m venv venv
   - Activate the environment:
     - Windows: environ\Scripts\activate
     - Linux/Mac: source environ/bin/activate
   - Install dependencies:
     > pip install -r requirements.txt
   - Configure database in `settings.py` with your MySQL credentials.
   - Run migrations:
     > python manage.py makemigrations
     > python manage.py migrate
   - Create a superuser (for admin access):
     > python manage.py createsuperuser
   - Start the server:
     > python manage.py runserver

3. Frontend Setup (React Native):
   - Navigate to the `frontend/` directory.
   - Install dependencies:
     > npm install
   - Start the app:
     > npm start
   - Run on emulator/device:
     - Android: npm run android
     - iOS: npm run ios

4. Firebase (for OTP/Authentication if configured):
   - Create a Firebase project at https://console.firebase.google.com/
   - Add Firebase credentials (google-services.json or GoogleService-Info.plist) in the app.
   - Enable Authentication (Email/OTP).

------------------------------------------------------------
🧪 Testing
------------------------------------------------------------
- The project includes test cases for user registration, login, profile creation, donor search, 
  and blood request features.
- To run Django backend tests:
  > python manage.py test

------------------------------------------------------------
📞 Support / Contact
------------------------------------------------------------
For any issues or confusion, contact:
Supervisor: Hasan Raza  
Email: HasanRaza@gcbskp.edu.pk  

------------------------------------------------------------
✅ Notes
------------------------------------------------------------
- Ensure MySQL server is running before backend setup.
- Internet connection is required for Firebase OTP authentication and donor-recipient communication.
- For smooth experience, test on both emulator and real device.

