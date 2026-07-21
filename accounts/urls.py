"""
Accounts App URLs
Handles user registration, authentication, profile management
"""
from django.urls import path
from . import views

#app_name = 'accounts'

urlpatterns = [
    # ==============================================
    # AUTHENTICATION
    # ==============================================
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ==============================================
    # PROFILE MANAGEMENT
    # ==============================================
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),  # ADD THIS LINE
    path('profile/update/', views.profile_update, name='profile_update'),
    path('profile/upload-document/', views.upload_document, name='upload_document'),
    path('profile/delete-document/<int:doc_id>/', views.delete_document, name='delete_document'),
    
    # ==============================================
    # DASHBOARD REDIRECT
    # ==============================================
    path('dashboard/', views.dashboard_redirect, name='dashboard'),
    
    # ==============================================
    # USER TYPE DASHBOARDS
    # ==============================================
    path('citizen-dashboard/', views.citizen_dashboard, name='citizen_dashboard'),
    path('employer-dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('agency-dashboard/', views.agency_dashboard, name='agency_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    
    # ==============================================
    # PASSWORD MANAGEMENT
    # ==============================================
    path('change-password/', views.change_password, name='change_password'),
    path('password-reset/', views.password_reset_request, name='password_reset'),
    path('password-reset-confirm/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # ==============================================
    # EMAIL VERIFICATION
    # ==============================================
    path('email-verify/<str:token>/', views.verify_email, name='verify_email'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification'),
    
    # ==============================================
    # ACCOUNT MANAGEMENT
    # ==============================================
    path('account/delete/', views.delete_account, name='delete_account'),
    path('account/suspend/', views.suspend_account, name='suspend_account'),
]