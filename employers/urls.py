"""
Employers App URLs
Handles employer registration, profile management, and dashboard
"""
from django.urls import path
from . import views

urlpatterns = [
    # Employer Listing
    path('employers/', views.employer_list, name='employers'),
    path('employers/<uuid:employer_id>/', views.employer_detail, name='employer_detail'),
    
    # Employer Registration & Setup
    path('employer/register/', views.employer_register, name='employer_register'),
    path('employer/setup/', views.employer_setup, name='employer_setup'),
    path('employer/verify/', views.employer_verification, name='employer_verification'),
    
    # Employer Profile Management
    path('employer/profile/update/', views.employer_profile_update, name='employer_profile_update'),
    path('employer/profile/logo-upload/', views.employer_logo_upload, name='employer_logo_upload'),
    
    # Employer Verification Documents
    path('employer/documents/upload/', views.upload_verification_documents, name='upload_verification_documents'),
    path('employer/documents/delete/<int:doc_id>/', views.delete_verification_document, name='delete_verification_document'),
    
    # Employer Dashboard Stats (AJAX)
    path('employer/stats/', views.employer_stats_ajax, name='employer_stats_ajax'),
]