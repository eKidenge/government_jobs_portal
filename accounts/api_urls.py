"""
Accounts App API URLs
"""
from django.urls import path
from .api_views import (
    UserRegistrationAPIView,
    UserLoginAPIView,
    UserProfileAPIView,
    UserUpdateAPIView,
    PasswordChangeAPIView,
    PasswordResetRequestAPIView,
    PasswordResetConfirmAPIView,
    EmailVerificationAPIView,
    ResendVerificationAPIView,
    UserDashboardStatsAPIView,
)

app_name = 'accounts_api'

urlpatterns = [
    # Authentication
    path('register/', UserRegistrationAPIView.as_view(), name='api_register'),
    path('login/', UserLoginAPIView.as_view(), name='api_login'),
    
    # Profile
    path('profile/', UserProfileAPIView.as_view(), name='api_profile'),
    path('profile/update/', UserUpdateAPIView.as_view(), name='api_profile_update'),
    
    # Password
    path('change-password/', PasswordChangeAPIView.as_view(), name='api_change_password'),
    path('password-reset/', PasswordResetRequestAPIView.as_view(), name='api_password_reset'),
    path('password-reset-confirm/', PasswordResetConfirmAPIView.as_view(), name='api_password_reset_confirm'),
    
    # Email Verification
    path('verify-email/<str:token>/', EmailVerificationAPIView.as_view(), name='api_verify_email'),
    path('resend-verification/', ResendVerificationAPIView.as_view(), name='api_resend_verification'),
    
    # Dashboard Stats
    path('dashboard-stats/', UserDashboardStatsAPIView.as_view(), name='api_dashboard_stats'),
]