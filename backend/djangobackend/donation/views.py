from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views import View
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from django.utils.decorators import method_decorator
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django_ratelimit.decorators import ratelimit
from rest_framework_simplejwt.tokens import RefreshToken
import secrets
import logging
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
# Removed csrf_exempt import - using JWT-only authentication

from .models import User, Profile, DonationRequest, CallLog, Message, Admin
from .serializers import (
    UserSerializer,
    SendOTPSerializer,
    OTPVerifySerializer,
    LoginSerializer,
    UserResponseSerializer,
    ProfileSerializer,
    DonationRequestSerializer,
    CallLogSerializer,
    MessageSerializer,
    DonationRequestResponseSerializer,
)
from .services import DonationRequestService, CallLogService, NotificationService

logger = logging.getLogger(__name__)

# =====================================================
# 🔹 ADMIN DECORATOR
# =====================================================

def admin_required(view_func):
    """Decorator to ensure only admin users can access the view"""
    def _wrapped_view(request, *args, **kwargs):
        # Check for JWT token in Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({"error": "Admin access required"}, status=403)
        
        try:
            from rest_framework_simplejwt.tokens import UntypedToken
            from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
            import jwt
            from django.conf import settings
            
            # Extract token
            token = auth_header.split(' ')[1]
            
            # Validate token
            UntypedToken(token)
            
            # Decode token to get user info
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_token.get('user_id')
            is_admin = decoded_token.get('is_admin', False)
            admin_id = decoded_token.get('admin_id')
            
            # Check if this is an admin token
            if is_admin and admin_id:
                try:
                    admin = Admin.objects.get(id=admin_id, is_active=True)
                    # Store admin info in request for use in view
                    request.admin = admin
                    return view_func(request, *args, **kwargs)
                except Admin.DoesNotExist:
                    return JsonResponse({"error": "Admin access required"}, status=403)
            else:
                return JsonResponse({"error": "Admin access required"}, status=403)
                
        except (InvalidToken, TokenError, jwt.DecodeError, jwt.ExpiredSignatureError):
            return JsonResponse({"error": "Invalid or expired token"}, status=401)
        except Exception as e:
            return JsonResponse({"error": "Admin access required"}, status=403)
        
    return _wrapped_view

# =====================================================
# 🔹 ADMIN PANEL VIEWS (Improved)
# =====================================================

@method_decorator(ratelimit(key='ip', rate='5/m'), name='dispatch')
class AdminLoginView(View):
    def post(self, request):
        # Handle both JSON and form data
        if request.content_type == 'application/json':
            import json
            try:
                data = json.loads(request.body)
                email = data.get("email", "").lower().strip()
                password = data.get("password", "")
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON"}, status=400)
        else:
            email = request.POST.get("email", "").lower().strip()
            password = request.POST.get("password", "")
        
        try:
            admin = Admin.objects.get(email=email, is_active=True)
            if admin.check_password(password):
                # Update last login
                from django.utils import timezone
                admin.last_login = timezone.now()
                admin.save()
                
                # Generate JWT tokens manually without using RefreshToken.for_user
                # to avoid database foreign key constraint issues
                from rest_framework_simplejwt.tokens import AccessToken
                from django.conf import settings
                import jwt
                from datetime import datetime, timedelta
                
                # Create custom JWT payload for admin
                import uuid
                
                access_jti = str(uuid.uuid4())
                refresh_jti = str(uuid.uuid4())
                
                payload = {
                    'user_id': admin.id + 10000,  # Offset to identify as admin
                    'email': admin.email,
                    'is_staff': True,
                    'is_admin': True,
                    'admin_id': admin.id,
                    'exp': datetime.utcnow() + timedelta(days=30),
                    'iat': datetime.utcnow(),
                    'jti': access_jti,
                    'token_type': 'access'
                }
                
                # Generate access token manually
                access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
                
                # Create refresh token payload
                refresh_payload = {
                    'user_id': admin.id + 10000,
                    'email': admin.email,
                    'is_admin': True,
                    'admin_id': admin.id,
                    'exp': datetime.utcnow() + timedelta(days=90),
                    'iat': datetime.utcnow(),
                    'jti': refresh_jti,
                    'token_type': 'refresh'
                }
                
                refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')
                
                # Store the refresh token in OutstandingToken for blacklisting
                try:
                    from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
                    from django.contrib.auth import get_user_model
                    
                    # Create a temporary user object for the token (required by OutstandingToken)
                    User = get_user_model()
                    temp_user, created = User.objects.get_or_create(
                        id=admin.id + 10000,
                        defaults={
                            'email': f'admin_{admin.id}@temp.local',
                            'name': f'Admin {admin.name}',
                            'is_active': False,  # Mark as inactive to avoid conflicts
                            'is_verified': True
                        }
                    )
                    
                    # Store the outstanding token
                    OutstandingToken.objects.create(
                        user=temp_user,
                        jti=refresh_jti,
                        token=refresh_token,
                        created_at=datetime.utcnow(),
                        expires_at=datetime.utcnow() + timedelta(days=90)
                    )
                except Exception as e:
                    # If storing fails, continue without it (logout will still work)
                    print(f"Failed to store outstanding token: {e}")
                
                return JsonResponse({
                    "message": "Admin logged in successfully",
                    "token": access_token,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {
                        "id": admin.id,
                        "name": admin.name,
                        "email": admin.email,
                        "is_staff": True,
                        "is_superuser": admin.is_superuser,
                        "is_active": admin.is_active
                    }
                })
            else:
                return JsonResponse({"error": "Invalid credentials"}, status=401)
        except Admin.DoesNotExist:
            return JsonResponse({"error": "Invalid credentials"}, status=401)
    
class AdminLogoutView(View):
    @method_decorator(ratelimit(key='ip', rate='5/m'))
    def post(self, request):
        # Handle both JSON and form data
        if request.content_type == 'application/json':
            import json
            try:
                data = json.loads(request.body)
                refresh_token = data.get("refresh_token")
            except json.JSONDecodeError:
                refresh_token = None
        else:
            refresh_token = request.POST.get("refresh_token")
        
        # Check for JWT token in Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Bearer '):
            try:
                from rest_framework_simplejwt.tokens import UntypedToken
                from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
                import jwt
                from django.conf import settings
                
                # Extract and validate access token
                token = auth_header.split(' ')[1]
                UntypedToken(token)
                
                # Decode token to get admin info
                decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                is_admin = decoded_token.get('is_admin', False)
                admin_id = decoded_token.get('admin_id')
                
                if is_admin and admin_id:
                    # Blacklist the refresh token if provided
                    if refresh_token:
                        try:
                            from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
                            from rest_framework_simplejwt.tokens import RefreshToken
                            
                            # Decode refresh token to get its jti
                            refresh_decoded = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
                            jti = refresh_decoded.get('jti')
                            
                            if jti:
                                # Try to find and blacklist the token
                                try:
                                    outstanding_token = OutstandingToken.objects.get(jti=jti)
                                    BlacklistedToken.objects.get_or_create(token=outstanding_token)
                                except OutstandingToken.DoesNotExist:
                                    # Token not found in outstanding tokens, that's okay
                                    pass
                        except Exception as e:
                            # If blacklisting fails, continue with logout
                            print(f"Token blacklisting failed: {e}")
                    
                    # Clear any session data if exists
                    request.session.flush()
                    
                    return JsonResponse({"message": "Admin logged out successfully"})
                else:
                    return JsonResponse({"error": "Invalid admin token"}, status=401)
                    
            except (InvalidToken, TokenError, jwt.InvalidTokenError) as e:
                return JsonResponse({"error": "Invalid token"}, status=401)
        
        # Fallback: check session-based auth (legacy)
        if request.session.get('admin_id'):
            request.session.flush()
            return JsonResponse({"message": "Admin logged out successfully"})
            
        return JsonResponse({"error": "Not authorized"}, status=401)


@method_decorator(ratelimit(key='ip', rate='5/m'), name='dispatch')
class AdminForgotPasswordView(View):
    def post(self, request):
        email = request.POST.get("email", "").lower().strip()
        try:
            admin = Admin.objects.get(email=email, is_active=True)
            otp = str(secrets.randbelow(900000) + 100000)  # Secure 6-digit OTP
            cache.set(f"admin_pw_reset_{email}", otp, timeout=600)  # 10 min expiry
            
            send_mail(
                "Admin Password Reset OTP",
                f"Your OTP is {otp}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False
            )
            return JsonResponse({"message": "OTP sent to email"})
        except Admin.DoesNotExist:
            return JsonResponse({"error": "Admin account not found"}, status=404)

@method_decorator(ratelimit(key='ip', rate='3/m'), name='dispatch')
class AdminCreateView(View):
    @method_decorator(admin_required)
    def post(self, request):
        # Admin authentication is handled by the admin_required decorator
        
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").lower().strip()
        password = request.POST.get("password", "")
        
        # Validation
        if not name or not email or not password:
            return JsonResponse({"error": "Name, email, and password are required"}, status=400)
        
        if len(password) < 8:
            return JsonResponse({"error": "Password must be at least 8 characters long"}, status=400)
        
        # Check if admin with this email already exists
        if Admin.objects.filter(email=email).exists():
            return JsonResponse({"error": "Admin with this email already exists"}, status=400)
        
        try:
            # Create new admin
            admin = Admin(
                name=name,
                email=email,
                is_active=True,
                is_superuser=False  # New admins are not superusers by default
            )
            admin.set_password(password)
            admin.save()
            
            return JsonResponse({
                "message": "Admin created successfully",
                "admin": {
                    "id": admin.id,
                    "name": admin.name,
                    "email": admin.email,
                    "is_active": admin.is_active,
                    "is_superuser": admin.is_superuser,
                    "date_joined": admin.date_joined.isoformat()
                }
            }, status=201)
        except Exception as e:
            return JsonResponse({"error": f"Failed to create admin: {str(e)}"}, status=500)

@method_decorator(ratelimit(key='ip', rate='5/m'), name='dispatch')
class AdminResetPasswordView(View):
    def post(self, request):
        email = request.POST.get("email", "").lower().strip()
        otp = request.POST.get("otp", "")
        new_password = request.POST.get("new_password", "")
        
        cached_otp = cache.get(f"admin_pw_reset_{email}")
        
        if cached_otp and cached_otp == otp:
            try:
                admin = Admin.objects.get(email=email, is_active=True)
                admin.set_password(new_password)
                admin.save()
                cache.delete(f"admin_pw_reset_{email}")
                return JsonResponse({"message": "Password reset successfully"})
            except Admin.DoesNotExist:
                return JsonResponse({"error": "Admin account not found"}, status=404)
        return JsonResponse({"error": "Invalid or expired OTP"}, status=400)

class UserListView(View):
    @method_decorator([admin_required, ratelimit(key='ip', rate='60/m')])
    def get(self, request):
        users = User.objects.filter(is_staff=False).values(
            'id', 'email', 'name', 'is_active', 'is_verified', 'date_joined'
        )
        return JsonResponse({'users': list(users)})

class UserDeleteView(View):
    @method_decorator([admin_required, ratelimit(key='ip', rate='30/m')])
    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk, is_staff=False)
            user.delete()
            return JsonResponse({'message': 'User deleted successfully'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

class BlockUnblockUserView(View):
    @method_decorator([admin_required, ratelimit(key='ip', rate='30/m')])
    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk, is_staff=False)
            user.is_active = not user.is_active
            user.save()
            status = 'unblocked' if user.is_active else 'blocked'
            return JsonResponse({'message': f'User {status} successfully'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

class RevokeAccessView(View):
    @method_decorator([admin_required, ratelimit(key='ip', rate='30/m')])
    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            if user.is_superuser:
                return JsonResponse(
                    {'error': 'Cannot revoke superuser access'}, 
                    status=403
                )
            user.is_staff = False
            user.save()
            return JsonResponse({'message': 'Staff access revoked'})
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)

# =====================================================
# 🔹 AUTH + OTP VIEWS (Model-Aligned)
# =====================================================

class UserCreate(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    @method_decorator(ratelimit(key='ip', rate='3/m'))
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['email'] = data.get('email', '').lower().strip()

        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            logger.error(f"Registration validation failed: {serializer.errors}")
            logger.error(f"Request data: {data}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.is_valid(raise_exception=True)
        
        if User.objects.filter(email=data['email']).exists():
            return Response(
                {"error": "Email is already registered"},
                status=status.HTTP_409_CONFLICT
            )

        user = serializer.save()
        try:
            raw_otp = user.generate_otp()  # Using model's method
            
            send_mail(
                "Verify Your Account",
                f"Your verification code: {raw_otp}",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False
            )
            
            return Response(
                {
                    "message": "Registration successful. Check email for OTP.",
                    "user_id": user.id,
                    "next_step": "verify-otp"
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            user.delete()  # Rollback user creation
            return Response(
                {"error": "Failed to complete registration"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
@api_view(["POST"])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='3/m')
def send_otp(request):
    data = request.data.copy()
    data['email'] = data.get('email', '').lower().strip()

    serializer = SendOTPSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    
    # Get the actual user instance
    try:
        user = User.objects.get(email=serializer.validated_data['email'])
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        raw_otp = user.generate_otp()  # Use your model's method
        
        send_mail(
            "Your Verification Code",
            f"Your OTP: {raw_otp}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False
        )
        
        return Response(
            {"message": "OTP sent successfully", "next_step": "verify-otp"},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"OTP send error: {str(e)}")
        return Response(
            {"error": "Failed to send OTP"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ratelimit(key='ip', rate='5/m'))
    def post(self, request):
        data = request.data.copy()
        data['email'] = data.get('email', '').lower().strip()

        serializer = OTPVerifySerializer(data=data)
        if not serializer.is_valid():
            logger.error(f"OTP verification validation failed: {serializer.errors}")
            logger.error(f"Request data: {data}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.validated_data['user']
        user_serializer = UserResponseSerializer(user)
        
        # Generate JWT tokens for automatic login
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        return Response(
            {
                "message": "Email verified successfully!",
                "user": user_serializer.data,
                "token": access_token,
                "access_token": access_token,
                "refresh_token": str(refresh),
                "next_step": "dashboard"
            },
            status=status.HTTP_200_OK
        )

# =====================================================
# 🔹 USER PASSWORD RESET VIEWS
# =====================================================

@method_decorator(ratelimit(key='ip', rate='5/m'), name='dispatch')
class UserForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get("email", "").lower().strip()
        
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email, is_staff=False)
            otp = str(secrets.randbelow(900000) + 100000)  # Secure 6-digit OTP
            cache.set(f"user_pw_reset_{email}", otp, timeout=600)  # 10 min expiry
            
            send_mail(
                "Password Reset OTP",
                f"Your password reset OTP is: {otp}. This OTP will expire in 10 minutes.",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False
            )
            return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User account not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Password reset email error: {str(e)}")
            return Response({"error": "Failed to send email"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@method_decorator(ratelimit(key='ip', rate='5/m'), name='dispatch')
class UserVerifyResetOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get("email", "").lower().strip()
        otp = request.data.get("otp", "")
        
        if not all([email, otp]):
            return Response({"error": "Email and OTP are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        cached_otp = cache.get(f"user_pw_reset_{email}")
        
        if cached_otp and cached_otp == otp:
            return Response({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(ratelimit(key='ip', rate='5/m'), name='dispatch')
class UserResetPasswordView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get("email", "").lower().strip()
        otp = request.data.get("otp", "")
        new_password = request.data.get("new_password", "")
        
        if not all([email, otp, new_password]):
            return Response({"error": "Email, OTP, and new password are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        cached_otp = cache.get(f"user_pw_reset_{email}")
        
        if cached_otp and cached_otp == otp:
            try:
                user = User.objects.get(email=email, is_staff=False)
                user.set_password(new_password)
                user.save()
                cache.delete(f"user_pw_reset_{email}")
                return Response({"message": "Password reset successful"}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "User account not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ratelimit(key='ip', rate='5/m'))
    def post(self, request):
        data = request.data.copy()
        data['email'] = data.get('email', '').lower().strip()

        serializer = LoginSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        user_serializer = UserResponseSerializer(user)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        return Response(
            {
                "message": "Login successful",
                "user": user_serializer.data,
                "token": access_token,
                "access_token": access_token,
                "refresh_token": str(refresh),
                "next_step": "dashboard"
            },
            status=status.HTTP_200_OK
        )


class LogoutView(APIView):
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='10/m'))
    def post(self, request):
        """Logout user by blacklisting refresh token."""
        try:
            refresh_token = request.data.get('refresh_token')
            
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(
                {"message": "Logout successful"},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST
            )


# =====================================================
# 🔹 PROFILE MANAGEMENT VIEWS
# =====================================================

class ProfileCreateView(APIView):
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='10/m'))
    def post(self, request):
        """Create or update user profile."""
        try:
            # Get user from email in request
            email = request.data.get('email')
            if not email:
                return Response(
                    {"error": "Email is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get or create profile
            profile, created = Profile.objects.get_or_create(user=user)
            
            # Update profile with request data
            serializer = ProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "message": "Profile created successfully" if created else "Profile updated successfully",
                        "profile": serializer.data
                    },
                    status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Profile creation error: {e}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProfileDetailView(APIView):
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='20/m'))
    def get(self, request, email=None):
        """Get user profile by email."""
        try:
            if not email:
                return Response(
                    {"error": "Email parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                user = User.objects.get(email=email)
                profile = Profile.objects.get(user=user)
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Profile.DoesNotExist:
                return Response(
                    {"error": "Profile not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = ProfileSerializer(profile)
            return Response(
                {"profile": serializer.data},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Profile retrieval error: {e}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )





class DonorSearchView(APIView):
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='30/m'))
    def get(self, request):
        try:
            blood_group = request.GET.get('blood_group')
            city = request.GET.get('city')
            
            if not blood_group or not city:
                return Response(
                    {"error": "Both blood_group and city parameters are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            # Filter profiles by blood group, city, and role='donor'
            donor_profiles = Profile.objects.filter(
                blood_group=blood_group,
                city=city,
                role='donor'
            ).select_related('user')
            
            # Serialize the donor profiles
            serializer = ProfileSerializer(donor_profiles, many=True)
            
            return Response(
                {
                    "success": True,
                    "message": f"Found {len(serializer.data)} donors",
                    "donors": serializer.data,
                    "search_criteria": {
                        "blood_group": blood_group,
                        "city": city
                    }
                },
                status=status.HTTP_200_OK,
            )
            
        except Exception as e:
            logger.error(f"Error searching donors: {str(e)}")
            return Response(
                {"error": "An error occurred while searching for donors"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DonationRequestCreateView(APIView):
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='10/m'))
    def post(self, request):
        try:
            serializer = DonationRequestSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                # Use service to create donation request with notifications
                donation_request = DonationRequestService.create_donation_request_with_notification(
                    requester=request.user,
                    donor=serializer.validated_data['donor'],
                    blood_group=serializer.validated_data['blood_group'],
                    urgency_level=serializer.validated_data.get('urgency_level', 'medium'),
                    notes=serializer.validated_data.get('notes', '')
                )
                
                return Response(
                    {
                        "success": True,
                        "message": "Donation request created and notification sent",
                        "donation_request_id": donation_request.id
                    },
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating donation request: {str(e)}")
            return Response(
                {"error": "An error occurred while creating donation request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DonationRequestListView(APIView):
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='30/m'))
    def get(self, request):
        try:
            user = request.user
            # Get requests made by user or received by user
            requests_made = DonationRequest.objects.filter(requester=user)
            requests_received = DonationRequest.objects.filter(donor=user)
            
            made_serializer = DonationRequestSerializer(requests_made, many=True)
            received_serializer = DonationRequestSerializer(requests_received, many=True)
            
            return Response(
                {
                    "success": True,
                    "requests_made": made_serializer.data,
                    "requests_received": received_serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error fetching donation requests: {str(e)}")
            return Response(
                {"error": "An error occurred while fetching donation requests"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DonationRequestResponseView(APIView):
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='20/m'))
    def post(self, request, request_id):
        try:
            donation_request = DonationRequest.objects.get(id=request_id)
            user = request.user
            
            # Check if user is authorized to respond
            if user != donation_request.requester and user != donation_request.donor:
                return Response(
                    {"error": "You are not authorized to respond to this request"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = DonationRequestResponseSerializer(data=request.data)
            if serializer.is_valid():
                response = serializer.validated_data['response']
                notes = serializer.validated_data.get('notes', '')
                
                # Update the appropriate response field
                if user == donation_request.requester:
                    donation_request.user_response = response
                elif user == donation_request.donor:
                    donation_request.donor_response = response
                
                # Update status based on responses
                donation_request.update_status()
                
                # Send notification to the other party
                DonationRequestService.send_response_notification(
                    donation_request=donation_request,
                    responder=user,
                    response=response,
                    notes=notes
                )
                
                return Response(
                    {
                        "success": True,
                        "message": "Response recorded and notification sent",
                        "status": donation_request.status
                    },
                    status=status.HTTP_200_OK
                )
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except DonationRequest.DoesNotExist:
            return Response(
                {"error": "Donation request not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error responding to donation request: {str(e)}")
            return Response(
                {"error": "An error occurred while processing response"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CallLogCreateView(APIView):
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='20/m'))
    def post(self, request):
        try:
            serializer = CallLogSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                # Use service to log call with potential follow-up notifications
                call_log = CallLogService.log_call_with_outcome(
                    caller=request.user,
                    recipient=serializer.validated_data['recipient'],
                    donation_request=serializer.validated_data.get('donation_request'),
                    duration=serializer.validated_data.get('duration', 0),
                    outcome=serializer.validated_data.get('outcome', 'completed'),
                    notes=serializer.validated_data.get('notes', '')
                )
                return Response(
                    {
                        "success": True,
                        "message": "Call logged successfully",
                        "call_log_id": call_log.id
                    },
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {"error": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating call log: {str(e)}")
            return Response(
                {"error": "An error occurred while creating call log"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MessageListView(APIView):
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='30/m'))
    def get(self, request):
        try:
            user = request.user
            messages = Message.objects.filter(recipient=user).order_by('-created_at')
            serializer = MessageSerializer(messages, many=True)
            
            return Response(
                {
                    "success": True,
                    "messages": serializer.data
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error fetching messages: {str(e)}")
            return Response(
                {"error": "An error occurred while fetching messages"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MessageMarkReadView(APIView):
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='30/m'))
    def post(self, request, message_id):
        try:
            message = Message.objects.get(id=message_id, recipient=request.user)
            message.mark_as_read()
            
            return Response(
                {
                    "success": True,
                    "message": "Message marked as read"
                },
                status=status.HTTP_200_OK
            )
        except Message.DoesNotExist:
            return Response(
                {"error": "Message not found"},
                status=status.HTTP_404_NOT_FOUND,
            )


class CallInitiateView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ratelimit(key='ip', rate='10/m'))
    def post(self, request):
        """Initiate a call and send messages to both parties."""
        try:
            donation_request_id = request.data.get('donation_request_id')
            caller_email = request.data.get('caller_email')
            receiver_email = request.data.get('receiver_email')

            if not all([donation_request_id, caller_email, receiver_email]):
                return Response(
                    {"error": "donation_request_id, caller_email, and receiver_email are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get the donation request
            try:
                donation_request = DonationRequest.objects.get(id=donation_request_id)
            except DonationRequest.DoesNotExist:
                return Response(
                    {"error": "Donation request not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Get caller and receiver users
            try:
                caller = User.objects.get(email=caller_email)
                receiver = User.objects.get(email=receiver_email)
            except User.DoesNotExist:
                return Response(
                    {"error": "Caller or receiver not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Initiate call with messages
            call_log = CallLog.initiate_call_with_messages(
                donation_request=donation_request,
                caller=caller,
                receiver=receiver
            )

            return Response(
                {
                    "message": "Call initiated successfully and messages sent to both parties",
                    "call_id": call_log.id,
                    "status": call_log.call_status
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(f"Error initiating call: {str(e)}")
            return Response(
                {"error": "Failed to initiate call"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CallConfirmView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ratelimit(key='ip', rate='20/m'))
    def post(self, request, call_id):
        """Confirm call completion by caller or receiver."""
        try:
            user_email = request.data.get('user_email')
            
            if not user_email:
                return Response(
                    {"error": "user_email is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get the call log
            try:
                call_log = CallLog.objects.get(id=call_id)
            except CallLog.DoesNotExist:
                return Response(
                    {"error": "Call log not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Get the user
            try:
                user = User.objects.get(email=user_email)
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Check if user is caller or receiver
            if user == call_log.caller:
                if call_log.caller_confirmed:
                    return Response(
                        {"message": "Call already confirmed by caller"},
                        status=status.HTTP_200_OK,
                    )
                call_log.confirm_by_caller()
                role = "caller"
            elif user == call_log.receiver:
                if call_log.receiver_confirmed:
                    return Response(
                        {"message": "Call already confirmed by receiver"},
                        status=status.HTTP_200_OK,
                    )
                call_log.confirm_by_receiver()
                role = "receiver"
            else:
                return Response(
                    {"error": "User is not part of this call"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            response_data = {
                "message": f"Call confirmed by {role}",
                "caller_confirmed": call_log.caller_confirmed,
                "receiver_confirmed": call_log.receiver_confirmed,
                "both_confirmed": call_log.both_confirmed
            }

            if call_log.both_confirmed:
                response_data["message"] = "Call completed! Both parties have confirmed. Count updated."
                response_data["confirmed_at"] = call_log.confirmed_at

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error confirming call: {str(e)}")
            return Response(
                {"error": "Failed to confirm call"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MonthlyTrackerView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ratelimit(key='ip', rate='30/m'))
    def get(self, request):
        """Get monthly donation tracker for a user."""
        try:
            user_email = request.query_params.get('user_email')
            
            if not user_email:
                return Response(
                    {"error": "user_email is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get the user
            try:
                user = User.objects.get(email=user_email)
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Get or create current month tracker
            from .models import MonthlyDonationTracker
            tracker, created = MonthlyDonationTracker.get_or_create_for_user_month(user)

            return Response(
                {
                    "user_email": user.email,
                    "month": tracker.month.strftime('%B %Y'),
                    "completed_calls_count": tracker.completed_calls_count,
                    "monthly_goal_completed": tracker.monthly_goal_completed,
                    "goal_completed_at": tracker.goal_completed_at,
                    "progress": f"{tracker.completed_calls_count}/3"
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Error getting monthly tracker: {str(e)}")
            return Response(
                {"error": "Failed to get monthly tracker"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            logger.error(f"Error marking message as read: {str(e)}")
            return Response(
                {"error": "An error occurred while updating message"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )