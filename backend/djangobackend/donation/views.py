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

from .models import User, Profile
from .serializers import (
    UserSerializer,
    SendOTPSerializer,
    OTPVerifySerializer,
    LoginSerializer,
    UserResponseSerializer,
    ProfileSerializer,
)

logger = logging.getLogger(__name__)

# =====================================================
# 🔹 ADMIN PANEL VIEWS (Improved)
# =====================================================

@method_decorator(ratelimit(key='ip', rate='5/m'), name='dispatch')
class AdminLoginView(View):
    def post(self, request):
        email = request.POST.get("email", "").lower().strip()
        password = request.POST.get("password", "")
        
        user = authenticate(request, email=email, password=password)
        
        if user and (user.is_superuser or user.is_staff):
            login(request, user)
            return JsonResponse({
                "message": "Admin logged in",
                "is_superuser": user.is_superuser
            })
        return JsonResponse({"error": "Invalid credentials"}, status=401)
    
class AdminLogoutView(View):
    @method_decorator(ratelimit(key='ip', rate='5/m'))
    def post(self, request):
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            logout(request)
            return JsonResponse({"message": "Admin logged out successfully"})
        return JsonResponse({"error": "Not authorized"}, status=401)


@method_decorator(ratelimit(key='ip', rate='5/m'), name='dispatch')
class AdminForgotPasswordView(View):
    def post(self, request):
        email = request.POST.get("email", "").lower().strip()
        try:
            user = User.objects.get(email=email, is_staff=True)
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
        except User.DoesNotExist:
            return JsonResponse({"error": "Admin account not found"}, status=404)

@method_decorator(ratelimit(key='ip', rate='5/m'), name='dispatch')
class AdminResetPasswordView(View):
    def post(self, request):
        email = request.POST.get("email", "").lower().strip()
        otp = request.POST.get("otp", "")
        new_password = request.POST.get("new_password", "")
        
        cached_otp = cache.get(f"admin_pw_reset_{email}")
        
        if cached_otp and cached_otp == otp:
            try:
                user = User.objects.get(email=email, is_staff=True)
                user.set_password(new_password)
                user.save()
                cache.delete(f"admin_pw_reset_{email}")
                return JsonResponse({"message": "Password reset successful"})
            except User.DoesNotExist:
                return JsonResponse({"error": "Admin account not found"}, status=404)
        return JsonResponse({"error": "Invalid or expired OTP"}, status=400)

# Admin permission check decorator
def admin_required(view_func):
    return user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url='/admin/login/'
    )(view_func)
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


class ProfileListView(APIView):
    permission_classes = [AllowAny]  # Change to IsAdminUser for production
    
    @method_decorator(ratelimit(key='ip', rate='30/m'))
    def get(self, request):
        """Get all profiles for admin panel."""
        try:
            profiles = Profile.objects.all().select_related('user').order_by('-created_at')
            serializer = ProfileSerializer(profiles, many=True)
            return Response(
                {
                    "profiles": serializer.data,
                    "count": profiles.count()
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Profile list error: {e}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProfileUpdateView(APIView):
    permission_classes = [AllowAny]
    
    @method_decorator(ratelimit(key='ip', rate='10/m'))
    def put(self, request, profile_id):
        """Update profile by ID."""
        try:
            try:
                profile = Profile.objects.get(id=profile_id)
            except Profile.DoesNotExist:
                return Response(
                    {"error": "Profile not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = ProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "message": "Profile updated successfully",
                        "profile": serializer.data
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Profile update error: {e}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProfileDeleteView(APIView):
    permission_classes = [AllowAny]  # Change to IsAdminUser for production
    
    @method_decorator(ratelimit(key='ip', rate='10/m'))
    def delete(self, request, profile_id):
        """Delete profile by ID."""
        try:
            try:
                profile = Profile.objects.get(id=profile_id)
            except Profile.DoesNotExist:
                return Response(
                    {"error": "Profile not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            profile.delete()
            return Response(
                {"message": "Profile deleted successfully"},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Profile deletion error: {e}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )