"""
Jobs App URLs
Handles job listings, applications, and management
"""
from django.urls import path
from . import views

# app_name = 'jobs'  # Comment this out

urlpatterns = [
    # Job Listings
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<uuid:job_id>/', views.job_detail, name='job_detail'),
    
    # Job Applications
    path('jobs/<uuid:job_id>/apply/', views.apply_to_job, name='apply_to_job'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('application/<uuid:app_id>/', views.application_detail, name='application_detail'),
    path('application/<uuid:app_id>/withdraw/', views.withdraw_application, name='withdraw_application'),
    
    # Browse by Country
    path('countries/', views.country_list, name='countries'),
    path('countries/<slug:country_slug>/', views.country_jobs, name='country_jobs'),
    
    # Browse by Category
    path('categories/', views.category_list, name='categories'),
    path('categories/<slug:category_slug>/', views.category_jobs, name='category_jobs'),
    
    # ==============================================
    # EMPLOYER JOB MANAGEMENT
    # ==============================================
    path('employer/jobs/', views.employer_job_list, name='employer_job_list'),
    path('employer/jobs/create/', views.create_job, name='create_job'),
    path('employer/jobs/<uuid:job_id>/edit/', views.edit_job, name='edit_job'),
    path('employer/jobs/<uuid:job_id>/delete/', views.delete_job, name='delete_job'),
    path('employer/jobs/<uuid:job_id>/toggle-status/', views.toggle_job_status, name='toggle_job_status'),
    path('employer/jobs/<uuid:job_id>/applications/', views.job_applications, name='job_applications'),
    
    # Application Status Management
    path('employer/application/<uuid:app_id>/update-status/', views.update_application_status, name='update_application_status'),
    path('employer/application/<uuid:app_id>/notes/', views.add_application_notes, name='add_application_notes'),
    path('employer/application/<uuid:app_id>/download-cv/', views.download_cv, name='download_cv'),
    
    # ==============================================
    # AJAX ENDPOINTS
    # ==============================================
    path('featured-jobs/', views.featured_jobs_ajax, name='featured_jobs_ajax'),
    path('job-stats/', views.job_statistics_ajax, name='job_statistics_ajax'),
]