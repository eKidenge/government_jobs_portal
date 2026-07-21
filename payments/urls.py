"""
Payments App URLs
"""
from django.urls import path
from . import views

app_name = 'payments'  # This is CRITICAL - defines the namespace

urlpatterns = [
    # ==============================================
    # PAYMENT PAGES
    # ==============================================
    path('payment/', views.payment_page, name='payment_page'),
    path('payment/initiate/', views.initiate_payment, name='initiate_payment'),
    path('payment/confirmation/<uuid:payment_id>/', views.payment_confirmation, name='payment_confirmation'),
    path('payment/success/<uuid:payment_id>/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    
    # ==============================================
    # PAYMENT HISTORY & RECEIPTS
    # ==============================================
    path('payment/history/', views.payment_history, name='payment_history'),
    path('payment/<uuid:payment_id>/receipt/', views.download_receipt, name='download_receipt'),
    path('payment/<uuid:payment_id>/receipt-view/', views.view_receipt, name='view_receipt'),
    
    # ==============================================
    # PAYMENT PLANS (AJAX)
    # ==============================================
    path('payment/plans/', views.payment_plans, name='payment_plans'),
    
    # ==============================================
    # PAYMENT STATUS (AJAX)
    # ==============================================
    path('payment/status/<uuid:payment_id>/', views.check_payment_status, name='check_payment_status'),
    path('payment/check-access/', views.check_access, name='check_access'),
    
    # ==============================================
    # M-PESA CALLBACKS
    # ==============================================
    path('payment/mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),
    path('payment/mpesa-result/', views.mpesa_result, name='mpesa_result'),
    path('payment/mpesa-timeout/', views.mpesa_timeout, name='mpesa_timeout'),
    
    # ==============================================
    # PAYMENT VERIFICATION (Admin)
    # ==============================================
    path('admin/payments/', views.admin_payments, name='admin_payments'),
    path('admin/payments/<uuid:payment_id>/', views.admin_payment_detail, name='admin_payment_detail'),
    path('admin/payments/verify/<uuid:payment_id>/', views.admin_verify_payment, name='admin_verify_payment'),
    path('admin/payments/refund/<uuid:payment_id>/', views.admin_refund_payment, name='admin_refund_payment'),
    
    # ==============================================
    # WEBHOOKS (External Services)
    # ==============================================
    path('webhooks/mpesa/', views.mpesa_webhook, name='mpesa_webhook'),
    path('webhooks/ecitizen/', views.ecitizen_webhook, name='ecitizen_webhook'),
    
    # ==============================================
    # INVOICES
    # ==============================================
    path('payment/invoice/<uuid:payment_id>/', views.generate_invoice, name='generate_invoice'),
    path('payment/invoice/<uuid:payment_id>/download/', views.download_invoice, name='download_invoice'),
    
    # ==============================================
    # SUBSCRIPTION MANAGEMENT
    # ==============================================
    path('subscription/', views.manage_subscription, name='manage_subscription'),
    path('subscription/cancel/', views.cancel_subscription, name='cancel_subscription'),
    path('subscription/renew/', views.renew_subscription, name='renew_subscription'),
    
    # ==============================================
    # REPORTS (Admin Only)
    # ==============================================
    path('admin/reports/payments/', views.payment_reports, name='payment_reports'),
    path('admin/reports/payments/export/', views.export_payments, name='export_payments'),
    path('admin/reports/revenue/', views.revenue_report, name='revenue_report'),
    
    # ==============================================
    # API ENDPOINTS (REST API)
    # ==============================================
    path('api/payments/initiate/', views.api_initiate_payment, name='api_initiate_payment'),
    path('api/payments/status/<uuid:payment_id>/', views.api_payment_status, name='api_payment_status'),
    path('api/payments/history/', views.api_payment_history, name='api_payment_history'),
    path('api/payments/verify/<uuid:payment_id>/', views.api_verify_payment, name='api_verify_payment'),
    
    # ==============================================
    # PAYMENT TESTS (Development Only)
    # ==============================================
    path('payment/test/mpesa/', views.test_mpesa, name='test_mpesa'),
    path('payment/test/success/', views.test_success, name='test_success'),
    path('payment/test/failure/', views.test_failure, name='test_failure'),
]