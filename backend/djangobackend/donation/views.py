from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.generics import ListAPIView, CreateAPIView

from .models import Admin1, Signup1
from .serializers import Admin1Serializer, Signup1Serializer


def home(request):
    return HttpResponse("Welcome to the Blood Donation App API")


class Admin1List(ListAPIView):
    queryset = Admin1.objects.all()
    serializer_class = Admin1Serializer


class Signup1Create(CreateAPIView):
    queryset = Signup1.objects.all()
    serializer_class = Signup1Serializer

class Signup1List(CreateAPIView):
    queryset = Signup1.objects.all()
    serializer_class = Signup1Serializer
