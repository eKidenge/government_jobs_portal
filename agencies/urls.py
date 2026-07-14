"""
Agencies App URLs (Recruitment Agencies)
Handles agency registration, verification, and management
"""
from django.urls import path
from . import views

urlpatterns = [
    # Agency Listing
    path('agencies/', views.agency_list, name='agencies'),
    path('agencies/<uuid:agency_id>/', views.agency_detail, name='agency_detail'),
    
    # Agency Registration & Setup
    path('agency/register/', views.agency_register, name='agency_register'),
    path('agency/setup/', views.agency_setup, name='agency_setup'),
    path('agency/verify/', views.agency_verification, name='agency_verification'),
    
    # Agency Profile Management
    path('agency/profile/update/', views.agency_profile_update, name='agency_profile_update'),
    path('agency/profile/logo-upload/', views.agency_logo_upload, name='agency_logo_upload'),
    
    # Agency Accreditation Documents
    path('agency/documents/upload/', views.upload_accreditation_documents, name='upload_accreditation_documents'),
    path('agency/documents/delete/<int:doc_id>/', views.delete_accreditation_document, name='delete_accreditation_document'),
    
    # Agency Jobs Management
    path('agency/jobs/', views.agency_job_list, name='agency_job_list'),
    path('agency/jobs/create/', views.agency_create_job, name='agency_create_job'),
    path('agency/jobs/<uuid:job_id>/edit/', views.agency_edit_job, name='agency_edit_job'),
    
    # Agency Dashboard Stats (AJAX)
    path('agency/stats/', views.agency_stats_ajax, name='agency_stats_ajax'),
]