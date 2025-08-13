from django.http import HttpResponse
from rest_framework.generics import ListAPIView, CreateAPIView
from .models import Admin1, Registration
from .serializers import Admin1Serializer, RegistrationSerializer
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


from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='3/m')  # Limit to 3 requests per minute
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
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


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """
    Verify OTP. Post body: { "user_id": <id>, "otp": "123456" } or { "email": "<email>", "otp": "123456" }
    """
    user_id = request.data.get('user_id')
    email = request.data.get('email')
    otp = request.data.get('otp')

    if not otp:
        return Response({"error": "OTP is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        if user_id:
            user = Registration.objects.get(pk=user_id)
        elif email:
            user = Registration.objects.get(email=email)
        else:
            return Response({"error": "Provide user_id or email"}, status=status.HTTP_400_BAD_REQUEST)
    except Registration.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    ok, msg = user.verify_otp(otp)
    if ok:
        return Response({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)
    else:
        return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

