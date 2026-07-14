"""
Jobs App API URLs
"""
from django.urls import path
from .api_views import (
    JobListView,
    JobDetailView,
    JobApplicationCreateView,
    MyApplicationsView,
    ApplicationDetailView,
    FeaturedJobsView,
    JobStatisticsView,
    JobCategoriesView,
    JobCountriesView,
    EmployerJobListView,
    EmployerJobCreateView,
    EmployerJobUpdateView,
    EmployerJobDeleteView,
    UpdateApplicationStatusView,
    EmployerDashboardStatsView,
    CountryJobsView,
    CategoryJobsView,
)

app_name = 'jobs_api'

urlpatterns = [
    # Job Listings
    path('', JobListView.as_view(), name='api_job_list'),
    path('<uuid:pk>/', JobDetailView.as_view(), name='api_job_detail'),
    
    # Job Applications
    path('<uuid:job_id>/apply/', JobApplicationCreateView.as_view(), name='api_apply_job'),
    path('my-applications/', MyApplicationsView.as_view(), name='api_my_applications'),
    path('applications/<uuid:pk>/', ApplicationDetailView.as_view(), name='api_application_detail'),
    
    # Featured & Statistics
    path('featured/', FeaturedJobsView.as_view(), name='api_featured_jobs'),
    path('statistics/', JobStatisticsView.as_view(), name='api_job_statistics'),
    path('categories/', JobCategoriesView.as_view(), name='api_job_categories'),
    path('countries/', JobCountriesView.as_view(), name='api_job_countries'),
    
    # Country & Category Filters
    path('countries/<slug:country_slug>/', CountryJobsView.as_view(), name='api_country_jobs'),
    path('categories/<slug:category_slug>/', CategoryJobsView.as_view(), name='api_category_jobs'),
    
    # Employer Job Management
    path('employer/jobs/', EmployerJobListView.as_view(), name='api_employer_jobs'),
    path('employer/jobs/create/', EmployerJobCreateView.as_view(), name='api_create_job'),
    path('employer/jobs/<uuid:pk>/update/', EmployerJobUpdateView.as_view(), name='api_update_job'),
    path('employer/jobs/<uuid:pk>/delete/', EmployerJobDeleteView.as_view(), name='api_delete_job'),
    
    # Application Status Management
    path('employer/applications/<uuid:pk>/status/', UpdateApplicationStatusView.as_view(), name='api_update_application_status'),
    path('employer/dashboard-stats/', EmployerDashboardStatsView.as_view(), name='api_employer_stats'),
]