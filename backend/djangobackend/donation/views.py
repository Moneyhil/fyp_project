from django.contrib.auth import authenticate, login, logout, get_user_model
from django.http import JsonResponse
from django.views import View
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django_ratelimit.decorators import ratelimit
import random

from .serializers import (
    UserSerializer,
    SendOTPSerializer,
    OTPVerifySerializer,
    LoginSerializer,
    UserResponseSerializer,
)

User = get_user_model()

# =====================================================
# 🔹 ADMIN PANEL VIEWS
# =====================================================

# --- Admin Login ---
class AdminLoginView(View):
    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(username=email, password=password)

        if user and user.is_superuser:  # only superuser = admin
            login(request, user)
            return JsonResponse({"message": "Admin logged in"})
        return JsonResponse({"error": "Invalid credentials"}, status=401)


# --- Admin Logout ---
class AdminLogoutView(View):
    def post(self, request):
        logout(request)
        return JsonResponse({"message": "Logged out successfully"})


# --- Forgot Password (send OTP) ---
otp_store = {}  # ⚠️ Temporary: Use DB or cache in production

class AdminForgotPasswordView(View):
    def post(self, request):
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email, is_superuser=True)
            otp = random.randint(100000, 999999)
            otp_store[email] = otp
            send_mail(
                "Admin Password Reset OTP",
                f"Your OTP is {otp}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
            )
            return JsonResponse({"message": "OTP sent to email"})
        except User.DoesNotExist:
            return JsonResponse({"error": "Admin not found"}, status=404)


# --- Reset Password ---
class AdminResetPasswordView(View):
    def post(self, request):
        email = request.POST.get("email")
        otp = request.POST.get("otp")
        new_password = request.POST.get("new_password")

        if otp_store.get(email) == int(otp):
            user = User.objects.get(email=email, is_superuser=True)
            user.set_password(new_password)
            user.save()
            del otp_store[email]
            return JsonResponse({"message": "Password reset successful"})
        return JsonResponse({"error": "Invalid OTP"}, status=400)


# --- List all users ---
class UserListView(View):
    def get(self, request):
        users = User.objects.filter(is_superuser=False).values(
            "id", "username", "email", "is_active"
        )
        return JsonResponse(list(users), safe=False)


# --- Delete user ---
class UserDeleteView(View):
    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk, is_superuser=False)
            user.delete()
            return JsonResponse({"message": "User deleted"})
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)


# --- Block/Unblock user ---
class BlockUnblockUserView(View):
    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk, is_superuser=False)
            user.is_active = not user.is_active
            user.save()
            return JsonResponse(
                {"message": f"User {'unblocked' if user.is_active else 'blocked'}"}
            )
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)


# --- Revoke Access (remove staff/admin privileges) ---
class RevokeAccessView(View):
    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk, is_superuser=False)
            user.is_staff = False
            user.save()
            return JsonResponse({"message": "Access revoked"})
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)


# =====================================================
# 🔹 AUTH + OTP VIEWS
# =====================================================

# Helper function to send OTP email
def send_verification_email(email, otp):
    subject = "Email Verification - Blood Donation App"
    message = f"""
    Thank you for registering with our Blood Donation App!

    Your verification code is: {otp}

    This code will expire in 10 minutes.

    If you didn't request this code, please ignore this email.

    Best regards,
    Blood Donation App Team
    """
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)


# --- Registration with OTP ---
class UserCreate(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get("email")
            if User.objects.filter(email=email).exists():
                return Response({"error": "Email is already registered"}, status=409)

            user = serializer.save()
            raw_otp = user.set_otp()  # assume set_otp() is in model

            try:
                send_verification_email(user.email, raw_otp)
            except Exception:
                return Response(
                    {
                        "message": "Registration successful (test mode). Use this OTP to verify.",
                        "user_id": user.id,
                        "email": user.email,
                        "temp_code": raw_otp,
                        "next_step": "verify-otp",
                    },
                    status=201,
                )

            return Response(
                {
                    "message": "Registration successful. Please check your email for OTP.",
                    "user_id": user.id,
                    "email": user.email,
                    "next_step": "verify-otp",
                },
                status=201,
            )

        return Response(serializer.errors, status=400)


# --- Resend OTP ---
@ratelimit(key="ip", rate="3/m")
@api_view(["POST"])
@permission_classes([AllowAny])
def send_otp(request):
    serializer = SendOTPSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        raw_otp = user.set_otp()

        try:
            send_verification_email(user.email, raw_otp)
            return Response({"message": "OTP sent successfully", "next_step": "verify-otp"}, status=200)
        except Exception:
            return Response(
                {
                    "message": "OTP generated (test mode). Use this temporary code.",
                    "temp_code": raw_otp,
                    "next_step": "verify-otp",
                },
                status=200,
            )

    return Response(serializer.errors, status=400)


# --- Verify OTP ---
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            user_serializer = UserResponseSerializer(user)
            return Response(
                {
                    "message": "Email verified successfully!",
                    "user": user_serializer.data,
                    "next_step": "profile",
                },
                status=200,
            )
        return Response(serializer.errors, status=400)


# --- User Login ---
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            user_serializer = UserResponseSerializer(user)
            return Response(
                {
                    "message": "Login successful",
                    "user": user_serializer.data,
                    "next_step": "profile",
                },
                status=200,
            )
        return Response(serializer.errors, status=400)
