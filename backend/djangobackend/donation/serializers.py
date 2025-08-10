from rest_framework import serializers
from .models import Admin1, Signup1
class Admin1Serializer(serializers.ModelSerializer):
    class Meta:
        model = Admin1
        fields = ['id' , 'first_name' , 'email', 'phone_number','password']
class Signup1Serializer(serializers.ModelSerializer):
    class Meta:
        model = Signup1
        fields = ['id', 'first_name', 'email', 'phone_number', 'password', 'confirmpassword']