from rest_framework import serializers
from .models import User, Profile
import re
from django.core.mail import send_mail
from django.conf import settings
import logging
from django.contrib.auth.password_validation import validate_password

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'is_verified']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_verified': {'read_only': True}
        }
        

    def validate_email(self, value):
        value = value.lower().strip()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already registered")
        return value
    

    def validate(self, attrs):
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )
        
        raw_otp = user.generate_otp()  # Using correct method name
        
        try:
            send_mail(
                subject='Verify Your Account',
                message=f'Your OTP: {raw_otp}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
        except Exception as e:
            logger.error(f"Email send failed: {e}")
        
        return user



class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')

        if not email or not otp:
            raise serializers.ValidationError({"error": "Email and OTP are required"})

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"error": "User not found", "code": "user_not_found"})

        if user.is_verified:
            attrs['user'] = user
            return attrs

        is_valid, message = user.verify_otp(otp)
        if not is_valid:
            error_code = "expired" if "expired" in message else "invalid"
            raise serializers.ValidationError({"error": message, "code": error_code})

        attrs['user'] = user
        return attrs


class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        self.user = user
        return value


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid password.")

        if not user.is_verified:
            raise serializers.ValidationError("User is not verified. Please verify your email first.")

        data['user'] = user
        return data


class UserResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "name", "email", "is_verified"]


class ProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'user_email', 'user_name', 'first_name', 'last_name', 
            'full_name', 'contact_number', 'address', 'gender', 'city', 
            'blood_group', 'role', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'user': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }
    
    def validate_contact_number(self, value):
        """Validate contact number format."""
        if value:
            clean_number = value.replace(' ', '').replace('-', '')
            if not re.match(r'^[+]?[0-9]{10,15}$', clean_number):
                raise serializers.ValidationError(
                    'Contact number must be 10-15 digits and may start with +'
                )
        return value
    
    def validate_first_name(self, value):
        """Validate first name contains only letters and spaces."""
        if value and not re.match(r'^[a-zA-Z\s]+$', value):
            raise serializers.ValidationError(
                'First name should only contain letters and spaces'
            )
        return value
    
    def validate_last_name(self, value):
        """Validate last name contains only letters and spaces."""
        if value and not re.match(r'^[a-zA-Z\s]+$', value):
            raise serializers.ValidationError(
                'Last name should only contain letters and spaces'
            )
        return value
    
    def validate_city(self, value):
        """Validate city name contains only letters and spaces."""
        if value and not re.match(r'^[a-zA-Z\s]+$', value):
            raise serializers.ValidationError(
                'City name should only contain letters and spaces'
            )
        return value
