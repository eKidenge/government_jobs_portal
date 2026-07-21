"""
Employers App URLs
Handles employer registration, profile management, and dashboard
"""
from django.urls import path
from . import views

app_name = 'employers'  # Add app_name for namespacing

urlpatterns = [
    # Employer Listing
    path('employers/', views.employer_list, name='employer_list'),
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
    
    # ============================================
    # JOB MANAGEMENT (for employer dashboard)
    # ============================================
    path('employer/jobs/', views.employer_job_list, name='employer_job_list'),
    path('employer/jobs/create/', views.create_job, name='create_job'),
    path('employer/jobs/<uuid:job_id>/edit/', views.edit_job, name='edit_job'),
    path('employer/jobs/<uuid:job_id>/applications/', views.job_applications, name='job_applications'),
    path('employer/jobs/<uuid:job_id>/delete/', views.delete_job, name='delete_job'),
    
    # ============================================
    # APPLICATION MANAGEMENT
    # ============================================
    path('employer/applications/<uuid:app_id>/update-status/', views.update_application_status, name='update_application_status'),
    path('employer/applications/<uuid:app_id>/view/', views.view_application, name='view_application'),
    path('employer/applications/bulk-action/', views.bulk_application_action, name='bulk_application_action'),
    
    # ============================================
    # EMPLOYER DASHBOARD
    # ============================================
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
]