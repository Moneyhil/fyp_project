from django.urls import path
from donation import views


urlpatterns = [
    path('admin1/', views.Admin1List.as_view()),
    path('Registration/create/', views.RegistrationCreate.as_view()),
    path('Registration/list/',views.RegistrationList.as_view()),
    path('send-otp/', views.signup, name='send-otp'),
    path('verify-otp/', views.verify_otp, name='verify-otp'),
]

