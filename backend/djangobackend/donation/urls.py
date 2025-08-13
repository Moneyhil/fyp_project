from django.urls import path
from donation import views


urlpatterns = [
    path('admin1/', views.Admin1List.as_view()),
    path('Registration/create/', views.RegistrationCreate.as_view()),
    path('Registration/list/',views.RegistrationList.as_view()),
    path('send-otp/', views.send_otp, name='send-otp'),
    path('login/', views.LoginView.as_view(), name='login'),
    path("verify-otp/",views.VerifyOTPView.as_view(), name="verify-otp"),
]

