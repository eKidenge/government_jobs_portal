"""
Agencies App API URLs (Recruitment Agencies)
"""
from django.urls import path
from .api_views import (
    AgencyListView,
    AgencyDetailView,
    AgencyRegisterView,
    AgencySetupView,
    AgencyVerificationView,
    AgencyProfileUpdateView,
    AgencyLogoUploadView,
    AgencyDocumentUploadView,
    AgencyDocumentDeleteView,
    AgencyJobsView,
    AgencyJobCreateView,
    AgencyJobUpdateView,
    AgencyStatsView,
)

app_name = 'agencies_api'

urlpatterns = [
    # Agency Listing
    path('', AgencyListView.as_view(), name='api_agency_list'),
    path('<uuid:pk>/', AgencyDetailView.as_view(), name='api_agency_detail'),
    
    # Registration & Setup
    path('register/', AgencyRegisterView.as_view(), name='api_agency_register'),
    path('setup/', AgencySetupView.as_view(), name='api_agency_setup'),
    path('verify/', AgencyVerificationView.as_view(), name='api_agency_verify'),
    
    # Profile Management
    path('profile/update/', AgencyProfileUpdateView.as_view(), name='api_agency_profile_update'),
    path('profile/logo/', AgencyLogoUploadView.as_view(), name='api_agency_logo_upload'),
    
    # Documents
    path('documents/upload/', AgencyDocumentUploadView.as_view(), name='api_agency_upload_document'),
    path('documents/<int:doc_id>/delete/', AgencyDocumentDeleteView.as_view(), name='api_agency_delete_document'),
    
    # Job Management
    path('jobs/', AgencyJobsView.as_view(), name='api_agency_jobs'),
    path('jobs/create/', AgencyJobCreateView.as_view(), name='api_agency_create_job'),
    path('jobs/<uuid:pk>/update/', AgencyJobUpdateView.as_view(), name='api_agency_update_job'),
    
    # Stats
    path('stats/', AgencyStatsView.as_view(), name='api_agency_stats'),
]