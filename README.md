# Blood Donation App - Enhanced Signup System

A comprehensive blood donation application with enhanced user registration, OTP authentication, and modern UI/UX.

## Features

### Frontend (React Native/Expo)
- **Enhanced Signup Screen**
  - Real-time form validation with Yup schema
  - Password strength indicator with visual feedback
  - Input icons and improved styling
  - Show/hide password toggles
  - Form validation with error messages
  - Loading states and disabled states
  - Keyboard avoiding behavior
  - Clear form functionality

- **OTP Verification Screen**
  - 6-digit OTP input with auto-focus
  - Auto-submit when all digits are entered
  - Resend OTP with countdown timer
  - Visual feedback for filled inputs
  - Error handling and display
  - Smooth animations and transitions
  - Back navigation

### Backend (Django REST Framework)
- **User Registration**
  - Secure password hashing
  - Email validation and uniqueness check
  - Password strength validation
  - Automatic OTP generation and email sending
  - Rate limiting for OTP requests

- **OTP Authentication**
  - Secure OTP generation using secrets
  - Email-based OTP delivery
  - OTP expiration (5 minutes)
  - Rate limiting (1 minute between requests)
  - Secure OTP verification

- **Database Models**
  - User registration with verification status
  - OTP management with timestamps
  - Admin user management

## API Endpoints

### Registration
- `POST /donation/Registration/create/` - Create new user account
- `POST /donation/send-otp/` - Send OTP to user email
- `POST /donation/verify-otp/` - Verify OTP and activate account
- `POST /donation/login/` - User login

### Admin
- `GET /donation/admin1/` - List admin users
- `POST /donation/admin1/` - Create admin user

## Installation & Setup

### Backend Setup
```bash
cd fyp_project/backend/djangobackend
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### Frontend Setup
```bash
cd fyp_project/frontend1
npm install
npx expo start
```

## Environment Configuration

### Backend (.env)
```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### Frontend (constants/API.js)
```javascript
export const API_BASE_URL = "http://192.168.100.16:8000";
```

## Password Requirements

The system enforces strong password requirements:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

## OTP System

### Features
- 6-digit numeric OTP
- 5-minute expiration
- Rate limiting (1 minute between requests)
- Secure hashing using SHA-256
- Email delivery with professional formatting

### Security Measures
- OTP hashing for storage
- Rate limiting to prevent abuse
- Automatic cleanup after verification
- Secure random generation using secrets module

## UI/UX Enhancements

### Signup Screen
- Modern card-based design
- Input icons for better visual hierarchy
- Real-time password strength indicator
- Smooth animations and transitions
- Responsive design for different screen sizes
- Clear error messaging
- Loading states with spinners

### OTP Screen
- Individual input boxes for each digit
- Auto-focus and navigation between inputs
- Visual feedback for filled inputs
- Countdown timer for resend functionality
- Professional email verification flow

## Error Handling

### Frontend
- Network error handling
- Validation error display
- Timeout handling
- User-friendly error messages
- Graceful degradation

### Backend
- Comprehensive error responses
- Field-specific validation errors
- Rate limiting error messages
- Database constraint handling
- Email delivery error handling

## Security Features

- Password hashing with Django's make_password
- OTP hashing for secure storage
- Rate limiting for API endpoints
- Input validation and sanitization
- CORS configuration
- Secure email delivery

## Dependencies

### Backend
- Django 4.x
- Django REST Framework
- django-ratelimit
- django-cors-headers

### Frontend
- React Native
- Expo
- Axios for API calls
- Yup for validation
- AsyncStorage for local storage
- Expo Vector Icons

## Usage Flow

1. **User Registration**
   - User fills out signup form
   - Real-time validation provides feedback
   - Password strength is checked
   - Form submission creates account and sends OTP

2. **Email Verification**
   - User receives OTP via email
   - Enters 6-digit code in OTP screen
   - Code is verified against stored hash
   - Account is activated upon successful verification

3. **Login**
   - User can login with email and password
   - Only verified accounts can login
   - Secure authentication process

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team.
