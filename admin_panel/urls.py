"""
Admin Panel App URLs
Handles government administration dashboard and management
"""
from django.urls import path
from . import views

app_name = 'admin_panel'  # COMMENT THIS OUT OR REMOVE IT

urlpatterns = [
    # ==============================================
    # DASHBOARD
    # ==============================================
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/stats/', views.dashboard_stats_ajax, name='dashboard_stats_ajax'),
    
    # ==============================================
    # JOB MANAGEMENT
    # ==============================================
    path('admin/jobs/', views.admin_job_list, name='admin_job_list'),
    path('admin/jobs/add/', views.admin_add_job, name='admin_add_job'),
    path('admin/jobs/<uuid:job_id>/edit/', views.admin_edit_job, name='admin_edit_job'),
    path('admin/jobs/<uuid:job_id>/delete/', views.admin_delete_job, name='admin_delete_job'),
    path('admin/jobs/<uuid:job_id>/approve/', views.admin_approve_job, name='admin_approve_job'),
    path('admin/jobs/<uuid:job_id>/reject/', views.admin_reject_job, name='admin_reject_job'),
    path('admin/jobs/<uuid:job_id>/feature/', views.admin_feature_job, name='admin_feature_job'),
    path('admin/jobs/bulk-action/', views.admin_bulk_job_action, name='admin_bulk_job_action'),
    path('admin/jobs/export/', views.admin_export_jobs, name='admin_export_jobs'),
    
    # ==============================================
    # EMPLOYER MANAGEMENT
    # ==============================================
    path('admin/employers/', views.admin_employer_list, name='admin_employer_list'),
    path('admin/employers/<uuid:employer_id>/', views.admin_employer_detail, name='admin_employer_detail'),
    path('admin/employers/<uuid:employer_id>/verify/', views.admin_verify_employer, name='admin_verify_employer'),
    path('admin/employers/<uuid:employer_id>/suspend/', views.admin_suspend_employer, name='admin_suspend_employer'),
    path('admin/employers/<uuid:employer_id>/activate/', views.admin_activate_employer, name='admin_activate_employer'),
    path('admin/employers/<uuid:employer_id>/renew-accreditation/', views.admin_renew_accreditation, name='admin_renew_accreditation'),
    path('admin/employers/<uuid:employer_id>/delete/', views.admin_delete_employer, name='admin_delete_employer'),
    path('admin/employers/register/', views.admin_register_employer, name='admin_register_employer'),
    path('admin/employers/<uuid:employer_id>/setup/', views.admin_employer_setup, name='admin_employer_setup'),
    
    # ==============================================
    # RECRUITMENT AGENCY MANAGEMENT
    # ==============================================
    path('admin/agencies/', views.admin_agency_list, name='admin_agency_list'),
    path('admin/agencies/<uuid:agency_id>/', views.admin_agency_detail, name='admin_agency_detail'),
    path('admin/agencies/<uuid:agency_id>/verify/', views.admin_verify_agency, name='admin_verify_agency'),
    path('admin/agencies/<uuid:agency_id>/suspend/', views.admin_suspend_agency, name='admin_suspend_agency'),
    path('admin/agencies/<uuid:agency_id>/activate/', views.admin_activate_agency, name='admin_activate_agency'),
    path('admin/agencies/<uuid:agency_id>/delete/', views.admin_delete_agency, name='admin_delete_agency'),
    path('admin/agencies/register/', views.admin_register_agency, name='admin_register_agency'),
    path('admin/agencies/<uuid:agency_id>/setup/', views.admin_agency_setup, name='admin_agency_setup'),
    
    # ==============================================
    # USER MANAGEMENT
    # ==============================================
    path('admin/users/', views.admin_user_list, name='admin_user_list'),
    path('admin/users/<uuid:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    path('admin/users/<uuid:user_id>/approve/', views.admin_approve_user, name='admin_approve_user'),
    path('admin/users/<uuid:user_id>/suspend/', views.admin_suspend_user, name='admin_suspend_user'),
    path('admin/users/<uuid:user_id>/activate/', views.admin_activate_user, name='admin_activate_user'),
    path('admin/users/<uuid:user_id>/reset-password/', views.admin_reset_user_password, name='admin_reset_user_password'),
    path('admin/users/<uuid:user_id>/delete/', views.admin_delete_user, name='admin_delete_user'),
    path('admin/users/bulk-action/', views.admin_bulk_user_action, name='admin_bulk_user_action'),
    
    # ==============================================
    # PAYMENT MANAGEMENT
    # ==============================================
    path('admin/payments/', views.admin_payment_list, name='admin_payment_list'),
    path('admin/payments/<uuid:payment_id>/', views.admin_payment_detail, name='admin_payment_detail'),
    path('admin/payments/<uuid:payment_id>/verify/', views.admin_verify_payment, name='admin_verify_payment'),
    path('admin/payments/<uuid:payment_id>/refund/', views.admin_refund_payment, name='admin_refund_payment'),
    path('admin/payments/export/', views.admin_export_payments, name='admin_export_payments'),
    
    # ==============================================
    # PAYMENT PLANS MANAGEMENT
    # ==============================================
    path('admin/payment-plans/', views.admin_payment_plans, name='admin_payment_plans'),
    path('admin/payment-plans/add/', views.admin_add_payment_plan, name='admin_add_payment_plan'),
    path('admin/payment-plans/<uuid:plan_id>/edit/', views.admin_edit_payment_plan, name='admin_edit_payment_plan'),
    path('admin/payment-plans/<uuid:plan_id>/delete/', views.admin_delete_payment_plan, name='admin_delete_payment_plan'),
    
    # ==============================================
    # CATEGORIES MANAGEMENT
    # ==============================================
    path('admin/categories/', views.admin_categories, name='admin_categories'),
    path('admin/categories/add/', views.admin_add_category, name='admin_add_category'),
    path('admin/categories/<uuid:category_id>/edit/', views.admin_edit_category, name='admin_edit_category'),
    path('admin/categories/<uuid:category_id>/delete/', views.admin_delete_category, name='admin_delete_category'),
    
    # ==============================================
    # COUNTRIES MANAGEMENT
    # ==============================================
    path('admin/countries/', views.admin_countries, name='admin_countries'),
    path('admin/countries/add/', views.admin_add_country, name='admin_add_country'),
    path('admin/countries/<uuid:country_id>/edit/', views.admin_edit_country, name='admin_edit_country'),
    path('admin/countries/<uuid:country_id>/delete/', views.admin_delete_country, name='admin_delete_country'),
    
    # ==============================================
    # REPORTS & ANALYTICS
    # ==============================================
    path('admin/reports/', views.admin_reports, name='admin_reports'),
    path('admin/reports/placements/', views.admin_placements_report, name='admin_placements_report'),
    path('admin/reports/jobs-by-country/', views.admin_jobs_by_country_report, name='admin_jobs_by_country_report'),
    path('admin/reports/jobs-by-sector/', views.admin_jobs_by_sector_report, name='admin_jobs_by_sector_report'),
    path('admin/reports/revenue/', views.admin_revenue_report, name='admin_revenue_report'),
    path('admin/reports/labour-migration/', views.admin_labour_migration_report, name='admin_labour_migration_report'),
    path('admin/reports/export/<str:report_type>/', views.admin_export_report, name='admin_export_report'),
    
    # ==============================================
    # SYSTEM SETTINGS
    # ==============================================
    path('admin/settings/', views.admin_settings, name='admin_settings'),
    path('admin/settings/update/', views.admin_update_settings, name='admin_update_settings'),
    
    # ==============================================
    # ADMIN PROFILE
    # ==============================================
    path('admin/profile/', views.admin_profile, name='admin_profile'),
    path('admin/profile/update/', views.admin_profile_update, name='admin_profile_update'),
    
    # ==============================================
    # ACTIVITY LOGS
    # ==============================================
    path('admin/activity-logs/', views.admin_activity_logs, name='admin_activity_logs'),
    path('admin/activity-logs/<uuid:log_id>/', views.admin_activity_log_detail, name='admin_activity_log_detail'),
    
    # ==============================================
    # ADMIN AJAX ENDPOINTS
    # ==============================================
    path('admin/ajax/job-status/<uuid:job_id>/', views.ajax_job_status, name='ajax_job_status'),
    path('admin/ajax/user-status/<uuid:user_id>/', views.ajax_user_status, name='ajax_user_status'),
    path('admin/ajax/employer-status/<uuid:employer_id>/', views.ajax_employer_status, name='ajax_employer_status'),
    path('admin/ajax/agency-status/<uuid:agency_id>/', views.ajax_agency_status, name='ajax_agency_status'),
]