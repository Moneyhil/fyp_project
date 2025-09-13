from django.http import JsonResponse
from django.views import View
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.utils import timezone
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
from django.utils.decorators import method_decorator

from .models import User, Profile, DonationRequest, CallLog, Admin, MonthlyDonationTracker
from .serializers import (
    UserSerializer,
    SendOTPSerializer,
    OTPVerifySerializer,
    LoginSerializer,
    UserResponseSerializer,
    ProfileSerializer,
    DonationRequestSerializer,
    CallLogSerializer,
    DonationRequestResponseSerializer,
)
from .services import DonationRequestService

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Simple health check endpoint"""
    if request.method == 'GET':
        return JsonResponse({
            'status': 'healthy',
            'message': 'Backend server is running'
        })
    return JsonResponse({'error': 'Method not allowed'}, status=405)


# ADMIN 

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
            
            
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_token.get('user_id')
            is_admin = decoded_token.get('is_admin', False)
            admin_id = decoded_token.get('admin_id')
            
            # Check if this is an admin token
            if is_admin and admin_id:
                try:
                    admin = Admin.objects.get(id=admin_id, is_active=True)
                    
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

# ADMIN PANEL

@method_decorator(ratelimit(key='ip', rate='5/m'), name='dispatch')
class AdminLoginView(View):
    def post(self, request):
        
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
                
                from rest_framework_simplejwt.tokens import AccessToken
                from django.conf import settings
                import jwt
                from datetime import datetime, timedelta
                
                import uuid
                
                access_jti = str(uuid.uuid4())
                refresh_jti = str(uuid.uuid4())
                
                payload = {
                    'user_id': admin.id + 10000,  
                    'email': admin.email,
                    'is_staff': True,
                    'is_admin': True,
                    'admin_id': admin.id,
                    'exp': datetime.utcnow() + timedelta(days=30),
                    'iat': datetime.utcnow(),
                    'jti': access_jti,
                    'token_type': 'access'
                }
                
        
                access_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
                
    
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
                
    
                try:
                    from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
                    from django.contrib.auth import get_user_model
                    
                    User = get_user_model()
                    temp_user, created = User.objects.get_or_create(
                        id=admin.id + 10000,
                        defaults={
                            'email': f'admin_{admin.id}@temp.local',
                            'name': f'Admin {admin.name}',
                            'is_active': False,  
                            'is_verified': True
                        }
                    )
                    
        
                    OutstandingToken.objects.create(
                        user=temp_user,
                        jti=refresh_jti,
                        token=refresh_token,
                        created_at=datetime.utcnow(),
                        expires_at=datetime.utcnow() + timedelta(days=90)
                    )
                except Exception as e:
        
                    print(f"Failed to store outstanding token: {e}")
                
                return JsonResponse({
                    "message": "Admin logged in successfully",
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

        if request.content_type == 'application/json':
            import json
            try:
                data = json.loads(request.body)
                refresh_token = data.get("refresh_token")
            except json.JSONDecodeError:
                refresh_token = None
        else:
            refresh_token = request.POST.get("refresh_token")
        
        
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
                                    
                                    pass
                        except Exception as e:
                            
                            print(f"Token blacklisting failed: {e}")
                    
                    return JsonResponse({"message": "Admin logged out successfully"})
                else:
                    return JsonResponse({"error": "Invalid admin token"}, status=401)
                    
            except (InvalidToken, TokenError, jwt.InvalidTokenError) as e:
                return JsonResponse({"error": "Invalid token"}, status=401)
            
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
                "Password Reset Code",
                f"Your password reset code: {otp}",
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
        
        
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").lower().strip()
        password = request.POST.get("password", "")
        
        # Validation
        if not name or not email or not password:
            return JsonResponse({"error": "Name, email, and password are required"}, status=400)
        
        if len(password) < 8:
            return JsonResponse({"error": "Password must be at least 8 characters long"}, status=400)
        
        
        if Admin.objects.filter(email=email).exists():
            return JsonResponse({"error": "Admin with this email already exists"}, status=400)
        
        try:
            # Create new admin
            admin = Admin(
                name=name,
                email=email,
                is_active=True,
                is_superuser=False  
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

class BlockedProfilesView(View):
    @method_decorator([admin_required, ratelimit(key='ip', rate='60/m')])
    def get(self, request):
    
        try:
            from django.utils import timezone
            
            
            current_month = timezone.now().date().replace(day=1)
            
            
            blocked_trackers = MonthlyDonationTracker.objects.filter(
                monthly_goal_completed=True,
                completed_calls_count__gte=3,
                
            ).select_related('user').order_by('-goal_completed_at')
            
            blocked_profiles = []
            for tracker in blocked_trackers:
                user = tracker.user
                
            
                is_currently_blocked = not user.is_active
                blocking_status = "Currently Blocked" if is_currently_blocked else "Previously Blocked (Unblocked)"
                
                blocked_profiles.append({
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'is_active': user.is_active,
                    'is_verified': user.is_verified,
                    'date_joined': user.date_joined,
                    'blocked_month': tracker.month,
                    'completed_calls_count': tracker.completed_calls_count,
                    'goal_completed_at': tracker.goal_completed_at,
                    'monthly_goal_completed': tracker.monthly_goal_completed,
                    'blocking_status': blocking_status,
                    'is_current_month': tracker.month == current_month
                })
            
            return JsonResponse({
                'blocked_profiles': blocked_profiles,
                'total_count': len(blocked_profiles)
            })
            
        except Exception as e:
            logger.error(f"Error fetching blocked profiles: {str(e)}")
            return JsonResponse({'error': 'Failed to fetch blocked profiles'}, status=500)

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


# AUTH + OTP 


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

        try:
            user = serializer.save()
            raw_otp = user.generate_otp()
            
            send_mail(
                "Email Verification Required",
                f"Your email verification code: {raw_otp}",
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
            return Response(
                {"error": "Registration failed. Please try again."},
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
    

    try:
        user = User.objects.get(email=serializer.validated_data['email'])
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        raw_otp = user.generate_otp()  # Use your model's method
        
        send_mail(
            "Email Verification Required",
            f"Your email verification code: {raw_otp}",
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
                "access_token": access_token,
                "refresh_token": str(refresh),
                "next_step": "dashboard"
            },
            status=status.HTTP_200_OK
        )

# USER PASSWORD RESET 


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
                "Password Reset Code",
                f"Your password reset code: {otp}. This OTP will expire in 10 minutes.",
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


# PROFILE MANAGEMENT


class ProfileCreateView(APIView):
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='10/m'))
    def post(self, request):
        """Create or update user profile."""
        try:

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
            
        
            profile, created = Profile.objects.get_or_create(user=user)
            
            
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
                # Use the serializer's save method which handles the requester assignment
                donation_request = serializer.save()
                
                return Response(
                    {
                        "success": True,
                        "message": "Donation request created successfully",
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
            
            
            if user != donation_request.requester and user != donation_request.donor:
                return Response(
                    {"error": "You are not authorized to respond to this request"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = DonationRequestResponseSerializer(data=request.data)
            if serializer.is_valid():
                response = serializer.validated_data['response']
                notes = serializer.validated_data.get('notes', '')
                
                
                if user == donation_request.requester:
                    donation_request.user_response = response
                    
                   
                    
                elif user == donation_request.donor:
                    donation_request.donor_response = response
                    
                
            
                donation_request.update_status()
                
              
                
                return Response(
                    {
                        "success": True,
                        "message": "Response recorded successfully",
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


class MonthlyTrackerView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ratelimit(key='ip', rate='30/m'))
    def get(self, request):
        """Get monthly donation tracker for a user."""
        try:
            
            logger.info(f"Monthly tracker request - Query params: {dict(request.query_params)}")
            logger.info(f"Request URL: {request.get_full_path()}")
            
            user_email = request.query_params.get('user_email')
            
            
            if not user_email or str(user_email).strip() in ['undefined', 'null', '']:
                logger.warning(f"Monthly tracker request missing or invalid user_email parameter. Received: '{user_email}'. Available params: {list(request.query_params.keys())}")
                return Response(
                    {
                        "error": "user_email is required",
                        "details": "Please provide user_email as a query parameter",
                        "example": "/donation/monthly-tracker/?user_email=user@example.com",
                        "received_params": list(request.query_params.keys()),
                        "received_email": user_email
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
    
            user_email = user_email.strip()
            if not user_email:
                logger.warning("Monthly tracker request with empty user_email parameter")
                return Response(
                    {
                        "error": "user_email cannot be empty",
                        "details": "Please provide a valid email address"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            # Basic email format validation
            if '@' not in user_email or '.' not in user_email:
                logger.warning(f"Invalid email format: {user_email}")
                return Response(
                    {
                        "error": "Invalid email format",
                        "details": "Please provide a valid email address"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        
            try:
                user = User.objects.get(email=user_email)
                logger.info(f"Found user for monthly tracker: {user.email}")
            except User.DoesNotExist:
                logger.warning(f"User not found for monthly tracker: {user_email}")
                return Response(
                    {"error": "User not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            
            from .models import MonthlyDonationTracker
            try:
                tracker, created = MonthlyDonationTracker.get_or_create_for_user_month(user)
                logger.info(f"Monthly tracker {'created' if created else 'retrieved'} for user {user.email}")
            except Exception as tracker_error:
                logger.error(f"Error creating/retrieving monthly tracker for {user.email}: {str(tracker_error)}")
                return Response(
                    {"error": "Failed to retrieve monthly tracker data"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            response_data = {
                "user_email": user.email,
                "month": tracker.month.strftime('%B %Y'),
                "completed_calls_count": tracker.completed_calls_count,
                "monthly_goal_completed": tracker.monthly_goal_completed,
                "goal_completed_at": tracker.goal_completed_at,
                "progress": f"{tracker.completed_calls_count}/3"
            }
            
            logger.info(f"Monthly tracker response for {user.email}: {response_data}")
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Unexpected error getting monthly tracker: {str(e)}")
            logger.error(f"Request details - Method: {request.method}, Path: {request.path}, Query params: {dict(request.query_params)}")
            return Response(
                {"error": "Failed to get monthly tracker"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
class DonorResponseView(APIView):

    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='10/m'))
    def get(self, request, request_id):
        response = request.GET.get('response')
        
        if response not in ['yes', 'no']:
            return Response(
                {"error": "Invalid response. Must be 'yes' or 'no'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            
            donation_request = DonationRequest.objects.get(id=request_id)
        except DonationRequest.DoesNotExist:
            return Response(
                {"error": "Donation request not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update donor response
        donor_agreed = response == 'yes'
        donation_request.donor_response = donor_agreed
        donation_request.update_status()
        donation_request.save()
 
        
        # Check if both parties have agreed
        if donation_request.user_response is True and donation_request.donor_response is True:
            donation_request.status = 'completed'
            donation_request.save()
            message = f"Thank you! Your response has been recorded. Both parties have agreed."
        else:
            message = f"Thank you for your response. You have responded '{response.upper()}' to the blood donation request."
        
        return Response({
            "message": message,
            "status": donation_request.status,
            "response_recorded": response
        })

class CallLogCreateView(APIView):
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='10/m'))
    def post(self, request):
        """Create a new call log entry."""
        try:
            serializer = CallLogSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                call_log = serializer.save()
                return Response(
                    {
                        "success": True,
                        "message": "Call log created successfully",
                        "call_id": call_log.id,
                        "call_log": CallLogSerializer(call_log).data
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


class SendDonorNotificationView(APIView):
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='10/m'))
    def post(self, request):
        """Send confirmation email to donor only when user selects 'yes' after call ends."""
        try:
            from .email_config import EmailService
            from django.utils import timezone
            
            call_log_id = request.data.get('call_log_id')
            donor_agreed = request.data.get('donor_agreed')  # True/False from frontend modal
            
            if not call_log_id:
                return Response(
                    {"error": "call_log_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                call_log = CallLog.objects.get(id=call_log_id)
            except CallLog.DoesNotExist:
                return Response(
                    {"error": "Call log not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Only send email if user agreed (selected 'yes')
            if donor_agreed is True:
                call_log.donor_email_response = 'yes'
                call_log.email_response_at = timezone.now()
                
                # Send donor confirmation email with increment functionality
                success, message = EmailService.send_donor_confirmation_email(
                    donor_user=call_log.receiver,
                    caller_user=call_log.caller,
                    call_log_id=call_log.id
                )
                
                if success:
                    call_log.email_sent = True
                    call_log.email_sent_at = timezone.now()
                    call_log.save()
                    
                    logger.info(f"Confirmation email sent to donor {call_log.receiver.email} for call {call_log.id}")
                    
                    return Response(
                        {
                            "success": True,
                            "message": "Donor confirmation email sent successfully"
                        },
                        status=status.HTTP_200_OK
                    )
                else:
                    logger.error(f"Failed to send confirmation email: {message}")
                    return Response(
                        {"error": f"Failed to send email: {message}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            else:
                # User selected 'no' - no email sent
                if donor_agreed is False:
                    call_log.donor_email_response = 'no'
                    call_log.email_response_at = timezone.now()
                    call_log.save()
                
                return Response(
                    {
                        "success": True,
                        "message": "No email sent - user declined donation request"
                    },
                    status=status.HTTP_200_OK
                )
            
        except Exception as e:
            logger.error(f"Error sending donor notification: {str(e)}")
            return Response(
                {"error": "An error occurred while sending notification"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DonorEmailConfirmationView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(ratelimit(key='ip', rate='20/m'))
    def get(self, request):
        try:
            call_log_id = request.GET.get('call_log_id')
            response = request.GET.get('response')
            
            if not call_log_id or not response:
                return Response(
                    {"error": "Missing call_log_id or response parameter"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if response not in ['yes', 'no']:
                return Response(
                    {"error": "Invalid response. Must be 'yes' or 'no'"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get the call log
            try:
                call_log = CallLog.objects.get(id=call_log_id)
            except CallLog.DoesNotExist:
                return Response(
                    {"error": "Call log not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
        
            call_log.donor_response = response
            call_log.save()
            
            count_completed = False
            
            if response == 'yes':
                    try:
                        from .models import MonthlyDonationTracker
                        tracker, created = MonthlyDonationTracker.get_or_create_for_user_month(
                            user=call_log.caller
                        )
                        goal_completed = tracker.increment_call_count()
                        count_completed = True
                        
                
                        if tracker.completed_calls_count >= 3 and not call_log.caller.is_active == False:
                            
                            call_log.caller.is_active = False
                            call_log.caller.save()
                            
                            logger.info(f"User {call_log.caller.email} blocked after completing monthly goal")
                            
            
                        logger.info(f"Count incremented for requester {call_log.caller.email}. New count: {tracker.completed_calls_count}")
                    except Exception as e:
                        logger.error(f"Error incrementing count: {str(e)}")
        
            if response == 'yes':
                try:
                    donation_request = DonationRequest.objects.get(
                        requester=call_log.requester,
                        donor=call_log.receiver,
                        user_response=True  
                    )
                    
                    if donation_request.status == 'pending':
                        donation_request.donor_response = True
                        donation_request.status = 'both_accepted'
                        donation_request.save()
                        logger.info(f"Updated donation request {donation_request.id} status to both_accepted")
                    elif donation_request.status == 'user_accepted':
                        donation_request.donor_response = True
                        donation_request.status = 'completed'
                        donation_request.save()
                        logger.info(f"Updated donation request {donation_request.id} status to completed")
                        
                except DonationRequest.DoesNotExist:
                    logger.warning(f"No matching donation request found for call {call_log.id} - but count was still incremented")
            
            
            if response == 'yes':
                if count_completed:
                    message = f"Dear {call_log.receiver.name}, your generosity means the world to us! Your agreement to donate blood has been recorded and one count has been completed for the requester. You are truly a hero - your donation will save lives. We will contact you soon with donation details. Thank you for being an angel! "
                else:
                    message = f"Dear {call_log.receiver.name}, thank you for agreeing to donate blood! Your response has been recorded. You are truly a hero - your donation will save lives. We will contact you soon with donation details."
            else:
                message = f"Thank you {call_log.receiver.name} for your response. We understand you cannot donate at this time."
            
            logger.info(f"Donor {call_log.receiver.email} responded '{response}' to call {call_log.id}. Count completed: {count_completed}")
            
            return Response({
                "success": True,
                "message": message,
                "response": response,
                "count_completed": count_completed,
                "donor_name": call_log.receiver.name,
                "call_id": call_log.id
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error processing email confirmation: {str(e)}")
            return Response(
                {"error": "An error occurred while processing confirmation"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProfileRedirectView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """Redirect to profile creation or dashboard."""
        return JsonResponse({
            "message": "Profile endpoint",
            "redirect": "/dashboard"
        })
