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


    path('registration/create/', views.UserCreate.as_view(), name='registration-create'),
    path('send-otp/', views.send_otp, name='send-otp'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # User password reset
    path('forgot-password/', views.UserForgotPasswordView.as_view(), name='user-forgot-password'),
    path('verify-reset-otp/', views.UserVerifyResetOTPView.as_view(), name='user-verify-reset-otp'),
    path('reset-password/', views.UserResetPasswordView.as_view(), name='user-reset-password'),
    
    # Profile management
    path('profile/create/', views.ProfileCreateView.as_view(), name='profile-create'),
    path('profile/<str:email>/', views.ProfileDetailView.as_view(), name='profile-detail'),
    path('profile/delete/<int:profile_id>/', views.ProfileDeleteView.as_view(), name='profile-delete'),
    
    # Donor search
    path('donors/search/', views.DonorSearchView.as_view(), name='donor-search'),
]

