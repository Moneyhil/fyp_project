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
    OTPVerifySerializer,
    SendOTPSerializer,
    UserResponseSerializer)
import re


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
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Check if email already exists
            email = serializer.validated_data.get('email')
            if Registration.objects.filter(email=email).exists():
                return Response(
                    {"error": "Email is already registered"}, 
                    status=status.HTTP_409_CONFLICT
                )
            
            # Create user
            user = serializer.save()
            
            # Generate and send OTP
            try:
                raw_otp = f'{secrets.randbelow(1000000):06d}'
                user.set_otp(raw_otp)
                
                # Send email with OTP
                self.send_otp_email(user.email, raw_otp)
                
                return Response({
                    "message": "Registration successful. Please check your email for verification code.",
                    "user_id": user.id,
                    "email": user.email
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                # If OTP sending fails, delete the user and return error
                user.delete()
                return Response(
                    {"error": "Failed to send verification code. Please try again."}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def send_otp_email(self, email, otp):
        """Send OTP email"""
        subject = 'Email Verification - Blood Donation App'
        message = f'''
        Thank you for registering with our Blood Donation App!
        
        Your verification code is: {otp}
        
        This code will expire in 5 minutes.
        
        If you didn't request this code, please ignore this email.
        
        Best regards,
        Blood Donation App creator
        '''
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False
        )


@ratelimit(key='ip', rate='3/m')  # Limit to 3 requests per minute
@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp(request):
    serializer = SendOTPSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        try:
            user = Registration.objects.get(email=email)
            raw_otp = f'{secrets.randbelow(1000000):06d}'  # Secure OTP
            user.set_otp(raw_otp)

            # Send email with OTP
            subject = 'Email Verification - Blood Donation App'
            message = f'''
            Your verification code is: {raw_otp}
            
            This code will expire in 5 minutes.
            
            If you didn't request this code, please ignore this email.
            
            Best regards,
            Blood Donation App Team
            '''
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False
            )
            return Response({"message": "OTP sent successfully"}, status=200)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            return Response({"error": "Failed to send OTP"}, status=500)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user_serializer = UserResponseSerializer(user)
            
            return Response({
                "message": "Email verified successfully!",
                "user": user_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            user_serializer = UserResponseSerializer(user)
            
            return Response({
                "message": "Login successful",
                "user": user_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

