"""
Agencies App URLs (Recruitment Agencies)
Handles agency registration, verification, and management
"""
from django.urls import path
from . import views

app_name = 'agencies'

urlpatterns = [
    # Agency Listing
    path('agencies/', views.agency_list, name='agency_list'),
    path('agencies/<uuid:agency_id>/', views.agency_detail, name='agency_detail'),
    path('agencies/<uuid:agency_id>/jobs/', views.agency_jobs_api, name='agency_jobs_api'),
    
    # Agency Registration & Setup
    path('agency/register/', views.agency_register, name='agency_register'),
    path('agency/setup/', views.agency_setup, name='agency_setup'),
    path('agency/verify/', views.agency_verification, name='agency_verification'),
    
    # Agency Profile Management
    path('agency/profile/update/', views.agency_profile_update, name='agency_profile_update'),
    path('agency/profile/logo-upload/', views.agency_logo_upload, name='agency_logo_upload'),
    
    # Agency Accreditation Documents - FIXED: Changed int to uuid
    path('agency/documents/upload/', views.upload_accreditation_documents, name='upload_accreditation_documents'),
    path('agency/documents/delete/<uuid:doc_id>/', views.delete_accreditation_document, name='delete_accreditation_document'),
    
    # Agency Jobs Management
    path('agency/jobs/', views.agency_job_list, name='agency_job_list'),
    path('agency/jobs/create/', views.agency_create_job, name='agency_create_job'),
    path('agency/jobs/<uuid:job_id>/edit/', views.agency_edit_job, name='agency_edit_job'),
    path('agency/jobs/<uuid:job_id>/delete/', views.agency_delete_job, name='agency_delete_job'),
    
    # Agency Dashboard
    path('agency/dashboard/', views.agency_dashboard, name='agency_dashboard'),
    
    # Agency Dashboard Stats (AJAX)
    path('agency/stats/', views.agency_stats_ajax, name='agency_stats_ajax'),
    
    # Admin Agency Management (for admin panel)
    path('admin/agencies/register/', views.admin_register_agency, name='admin_register_agency'),
    path('admin/agencies/<uuid:agency_id>/setup/', views.admin_agency_setup, name='admin_agency_setup'),
    path('admin/agencies/<uuid:agency_id>/stats/', views.admin_agency_stats, name='admin_agency_stats'),
]