from django.urls import path
from donation import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [

    path("admin-login/", views.AdminLoginView.as_view(), name="admin-login"),
    path("admin-logout/", views.AdminLogoutView.as_view(), name="admin-logout"),
    path("admin-create/", views.AdminCreateView.as_view(), name="admin-create"),
    path("admin-forgot-password/", views.AdminForgotPasswordView.as_view(), name="admin-forgot-password"),
    path("admin-reset-password/", views.AdminResetPasswordView.as_view(), name="admin-reset-password"),
    
    # user management
    path("admin/users/", views.UserListView.as_view(), name="user-list"),
    path("admin/users/<int:pk>/delete/", views.UserDeleteView.as_view(), name="user-delete"),
    path("admin/users/<int:pk>/block/", views.BlockUnblockUserView.as_view(), name="user-block-unblock"),
    path("admin/users/<int:pk>/revoke/", views.RevokeAccessView.as_view(), name="user-revoke"),
    path('admin/blocked-profiles/', views.BlockedProfilesView.as_view(), name='blocked_profiles'),


    path('registration/create/', views.UserCreate.as_view(), name='registration-create'),
    path('send-otp/', views.send_otp, name='send-otp'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify-otp'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # JWT Token endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # User password reset
    path('forgot-password/', views.UserForgotPasswordView.as_view(), name='user-forgot-password'),
    path('verify-reset-otp/', views.UserVerifyResetOTPView.as_view(), name='user-verify-reset-otp'),
    path('reset-password/', views.UserResetPasswordView.as_view(), name='user-reset-password'),
    
    # Profile management
    path('profile/create/', views.ProfileCreateView.as_view(), name='profile-create'),
    path('profile/<str:email>/', views.ProfileDetailView.as_view(), name='profile-detail'),
    
    # Donor search
    path('donors/search/', views.DonorSearchView.as_view(), name='donor-search'),
    
    # Donation requests
    path('donation-requests/create/', views.DonationRequestCreateView.as_view(), name='donation-request-create'),
    path('donation-requests/', views.DonationRequestListView.as_view(), name='donation-request-list'),
    path('donation-requests/<int:request_id>/respond/', views.DonationRequestResponseView.as_view(), name='donation-request-respond'),
    
    # Monthly tracking
    path('monthly-tracker/', views.MonthlyTrackerView.as_view(), name='monthly-tracker'),
    
    # Donor Response
    path('donor-response/<int:request_id>/<str:response>/', views.DonorResponseView.as_view(), name='donor-response'),
    
    # Call logs and notifications
    path('call-logs/create/', views.CallLogCreateView.as_view(), name='call-log-create'),
    path('messages/send-donor-notification/', views.SendDonorNotificationView.as_view(), name='send-donor-notification'),
    path('confirm-donation/', views.DonorEmailConfirmationView.as_view(), name='donor-email-confirmation'),
]

