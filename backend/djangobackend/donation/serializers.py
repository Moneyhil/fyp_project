from rest_framework import serializers
from .models import Admin1, Registration
import secrets  # For secure OTP generation
from django.core.mail import send_mail

class RegistrationSerializer(serializers.ModelSerializer):
    confirmpassword = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Registration
        fields = ['id', 'name', 'email', 'password', 'confirmpassword', 'is_verified']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_verified': {'read_only': True}
        }

    def validate(self, data):
        if data['password'] != data['confirmpassword']:
            raise serializers.ValidationError({"confirmpassword": "Passwords must match."})
        if len(data['password']) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirmpassword')
        user = Registration(**validated_data)

        # Generate cryptographically secure OTP
        otp_code = str(secrets.randbelow(900000) + 100000)  # 6-digit OTP
        user.set_otp(otp_code)
        user.save()

        # Send OTP via email (example)
        send_mail(
            'Your OTP Code',
            f'Your OTP is: {otp_code}',
            'noreply@yourdomain.com',
            [user.email],
            fail_silently=False,
        )
        return user