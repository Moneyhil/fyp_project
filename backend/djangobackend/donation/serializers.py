from rest_framework import serializers
from .models import Admin1, Registration
import re
from django.core.mail import send_mail
from django.conf import settings
import random



class Admin1Serializer(serializers.ModelSerializer):
    confirmpassword = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = Admin1
        fields = ['id', 'first_name', 'email', 'phone_number', 'password', 'confirmpassword']

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('confirmpassword'):
            raise serializers.ValidationError("Passwords do not match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirmpassword')
        return Admin1.objects.create(**validated_data)


class RegistrationSerializer(serializers.ModelSerializer):
    confirmpassword = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Registration
        fields = ['id', 'name', 'email', 'password', 'confirmpassword', 'is_verified']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_verified': {'read_only': True}
        }

    def validate(self, attrs):
        # Check if passwords match
        if attrs.get('password') != attrs.get('confirmpassword'):
            raise serializers.ValidationError({"confirmpassword": "Passwords do not match"})
        
        # Validate password strength
        password = attrs.get('password')
        if len(password) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long"})
        if not re.search(r'[A-Z]', password):
            raise serializers.ValidationError({"password": "Password must contain at least one uppercase letter"})
        if not re.search(r'[a-z]', password):
            raise serializers.ValidationError({"password": "Password must contain at least one lowercase letter"})
        if not re.search(r'\d', password):
            raise serializers.ValidationError({"password": "Password must contain at least one number"})
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise serializers.ValidationError({"password": "Password must contain at least one special character"})
        
        # Validate name format
        name = attrs.get('name')
        if not re.match(r'^[a-zA-Z\s]+$', name):
            raise serializers.ValidationError({"name": "Name can only contain letters and spaces"})
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirmpassword')
        user = Registration.objects.create(**validated_data)

        # Generate OTP
        raw_otp = str(random.randint(100000, 999999))
        user.set_otp(raw_otp)

        # Send OTP email
        send_mail(
            subject='Your OTP Code',
            message=f'Your OTP is {raw_otp}. It will expire in 5 minutes.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return user



class UserResponseSerializer(serializers.ModelSerializer):
    """Serializer for user data in responses"""
    class Meta:
        model = Registration
        fields = ['id', 'name', 'email', 'is_verified']


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError({"error": "Email and password are required"})

        try:
            user = Registration.objects.get(email=email)
        except Registration.DoesNotExist:
            raise serializers.ValidationError({"error": "Invalid credentials"})

        # Check password
        if not user.check_password(password):
            raise serializers.ValidationError({"error": "Invalid credentials"})

        # Check if user is verified
        if not user.is_verified:
            raise serializers.ValidationError({"error": "Please verify your email before logging in"})

        attrs['user'] = user
        return attrs


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')

        if not email or not otp:
            raise serializers.ValidationError({"error": "Email and OTP are required"})

        try:
            user = Registration.objects.get(email=email)
        except Registration.DoesNotExist:
            raise serializers.ValidationError({"error": "User not found"})

        # Verify OTP
        is_valid, message = user.verify_otp(otp)
        
        if not is_valid:
            raise serializers.ValidationError({"error": message})

        attrs['user'] = user
        return attrs


class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = Registration.objects.get(email=value)
        except Registration.DoesNotExist:
            raise serializers.ValidationError("User not found")
        return value