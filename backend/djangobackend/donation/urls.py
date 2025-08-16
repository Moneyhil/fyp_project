from django.urls import path
from donation import views

urlpatterns = [

    path("admin-login/", views.AdminLoginView.as_view(), name="admin-login"),
    path("admin-logout/", views.AdminLogoutView.as_view(), name="admin-logout"),
    path("admin-forgot-password/", views.AdminForgotPasswordView.as_view(), name="admin-forgot-password"),
    path("admin-reset-password/", views.AdminResetPasswordView.as_view(), name="admin-reset-password"),
    
    # user management
    path("admin/users/", views.UserListView.as_view(), name="user-list"),
    path("admin/users/<int:pk>/delete/", views.UserDeleteView.as_view(), name="user-delete"),
    path("admin/users/<int:pk>/block/", views.BlockUnblockUserView.as_view(), name="user-block-unblock"),
    path("admin/users/<int:pk>/revoke/", views.RevokeAccessView.as_view(), name="user-revoke"),


    path('user/create/', views.UserCreate.as_view(), name='registration-create'),
    path('send-otp/', views.send_otp, name='send-otp'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', views.LoginView.as_view(), name='login'),
]

