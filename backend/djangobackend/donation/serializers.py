from rest_framework import serializers
from .models import User
import re
from django.core.mail import send_mail
from django.conf import settings

class UserSerializer(serializers.ModelSerializer):
    confirmpassword = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
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

        # Check duplicate email
        if User.objects.filter(email=attrs.get("email")).exists():
            raise serializers.ValidationError({"email": "This email is already registered."})

        return attrs

    def create(self, validated_data):
        validated_data.pop('confirmpassword')
        password = validated_data.pop("password")

        # Create user via CustomUser manager
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=password
        )

        # Generate OTP
        raw_otp = user.set_otp()

        # Send OTP email
        try:
            send_mail(
                subject='Your OTP Code',
                message=f'Your OTP is {raw_otp}. It will expire in 10 minutes.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception:
            pass  # fallback: return OTP in API response in view

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
