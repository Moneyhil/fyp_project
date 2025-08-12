from rest_framework import serializers
from .models import Admin1, Registration

class Admin1Serializer(serializers.ModelSerializer):
    class Meta:
        model = Admin1
        fields = ['id', 'first_name', 'email', 'phone_number']

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
        # Create and return the user; OTP generation and email sending are handled in the view
        return Registration.objects.create(**validated_data)