"""
Employers App API URLs
"""
from django.urls import path
from .api_views import (
    EmployerListView,
    EmployerDetailView,
    EmployerRegisterView,
    EmployerSetupView,
    EmployerVerificationView,
    EmployerProfileUpdateView,
    EmployerLogoUploadView,
    EmployerDocumentUploadView,
    EmployerDocumentDeleteView,
    EmployerStatsView,
)

app_name = 'employers_api'

urlpatterns = [
    # Employer Listing
    path('', EmployerListView.as_view(), name='api_employer_list'),
    path('<uuid:pk>/', EmployerDetailView.as_view(), name='api_employer_detail'),
    
    # Registration & Setup
    path('register/', EmployerRegisterView.as_view(), name='api_employer_register'),
    path('setup/', EmployerSetupView.as_view(), name='api_employer_setup'),
    path('verify/', EmployerVerificationView.as_view(), name='api_employer_verify'),
    
    # Profile Management
    path('profile/update/', EmployerProfileUpdateView.as_view(), name='api_employer_profile_update'),
    path('profile/logo/', EmployerLogoUploadView.as_view(), name='api_employer_logo_upload'),
    
    # Documents
    path('documents/upload/', EmployerDocumentUploadView.as_view(), name='api_employer_upload_document'),
    path('documents/<int:doc_id>/delete/', EmployerDocumentDeleteView.as_view(), name='api_employer_delete_document'),
    
    # Stats
    path('stats/', EmployerStatsView.as_view(), name='api_employer_stats'),
]