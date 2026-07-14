"""
Payments App API URLs
"""
from django.urls import path
from .api_views import (
    PaymentPlansView,
    InitiatePaymentView,
    PaymentStatusView,
    PaymentHistoryView,
    PaymentReceiptView,
    MpesaCallbackView,
    AdminPaymentVerifyView,
    AdminPaymentRefundView,
)

app_name = 'payments_api'

urlpatterns = [
    # Payment Plans
    path('plans/', PaymentPlansView.as_view(), name='api_payment_plans'),
    
    # Payment Operations
    path('initiate/', InitiatePaymentView.as_view(), name='api_initiate_payment'),
    path('status/<uuid:payment_id>/', PaymentStatusView.as_view(), name='api_payment_status'),
    path('history/', PaymentHistoryView.as_view(), name='api_payment_history'),
    path('<uuid:payment_id>/receipt/', PaymentReceiptView.as_view(), name='api_payment_receipt'),
    
    # M-Pesa Callbacks (Webhooks)
    path('mpesa-callback/', MpesaCallbackView.as_view(), name='api_mpesa_callback'),
    
    # Admin Operations
    path('admin/verify/<uuid:payment_id>/', AdminPaymentVerifyView.as_view(), name='api_verify_payment'),
    path('admin/refund/<uuid:payment_id>/', AdminPaymentRefundView.as_view(), name='api_refund_payment'),
]