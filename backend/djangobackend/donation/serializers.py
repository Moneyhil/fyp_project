from rest_framework import serializers
from .models import Admin1, Registration, login, OTP
import secrets  # For secure OTP generation
from django.core.mail import send_mail
from django.contrib.auth import authenticate


class Admin1Serializer(serializers.ModelSerializer):
    confirmpassword = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = Admin1
        fields = ['id', 'first_name', 'email', 'phone_number', 'password']

class RegistrationSerializer(serializers.ModelSerializer):
    confirmpassword = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Registration
        fields = ['id', 'name', 'email', 'password', 'confirmpassword', 'is_verified']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_verified': {'read_only': True}
        }

    def create(self, validated_data):
        validated_data.pop('confirmpassword')

       
        return Registration.objects.create(**validated_data)
        return user
    

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(email=email, password=password)

        if not user:
            raise serializers.ValidationError({"error": "Invalid credentials"})

        if not user.is_verified:
            raise serializers.ValidationError({"error": "Please verify your account before logging in"})

        attrs['user'] = user
        return attrs


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get("email")
        otp_code = attrs.get("otp")

        try:
            user = login.objects.get(email=email)
        except login.DoesNotExist:
            raise serializers.ValidationError({"error": "User not found"})

        try:
            otp = OTP.objects.filter(user=user, code=otp_code).latest('created_at')
        except OTP.DoesNotExist:
            raise serializers.ValidationError({"error": "Invalid OTP"})

        if otp.is_expired():
            raise serializers.ValidationError({"error": "OTP expired"})

        attrs["user"] = user
        attrs["otp"] = otp
        return attrs