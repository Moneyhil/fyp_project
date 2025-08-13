from django.http import HttpResponse
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.views import APIView
from .models import Admin1, Registration
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
import random
from django.utils import timezone
import datetime
from django.contrib.auth.hashers import make_password
import secrets
from django_ratelimit.decorators import ratelimit
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    Admin1Serializer, 
    RegistrationSerializer, 
    LoginSerializer, 
    OTPVerifySerializer)


def home(request):
    return HttpResponse("Welcome to the Blood Donation App API")


# Admin endpoints
class Admin1List(ListAPIView):
    queryset = Admin1.objects.all()
    serializer_class = Admin1Serializer


# Registration endpoints
class RegistrationCreate(CreateAPIView):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer


class RegistrationList(ListAPIView):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer


@ratelimit(key='ip', rate='3/m')  # Limit to 3 requests per minute
@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    email = request.data.get('email')
    if not email:
        return Response({"error": "Email is required"}, status=400)

    try:
        user = Registration.objects.get(email=email)
    except Registration.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    raw_otp = f'{secrets.randbelow(1000000):06d}'  # Secure OTP
    user.set_otp(raw_otp)

    try:
        send_mail(
            'Your OTP Code',
            f'Your OTP is {raw_otp}. Valid for 5 minutes.',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False
        )
        return Response({"message": "OTP sent successfully"}, status=200)
    except Exception as e:
        return Response({"error": "Failed to send OTP"}, status=500)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            otp = serializer.validated_data["otp"]

            # Mark user as verified
            user.is_verified = True
            user.save()

            # Delete OTP after successful verification
            otp.delete()

            # Auto-login after verification
            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "OTP verified successfully",
                "token": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "name": user.first_name,
                    "email": user.email
                }
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "Login successful",
                "token": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "name": user.first_name,
                    "email": user.email
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

