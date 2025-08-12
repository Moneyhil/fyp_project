from rest_framework import serializers
from .models import Admin1, Registration
import secrets  # For secure OTP generation
from django.core.mail import send_mail


class Admin1Serializer(serializers.ModelSerializer):
    confirmpassword = serializers.CharField(write_only=True, required=True)

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