"""
Payments App URLs
"""
from django.urls import path
from . import views

urlpatterns = [
    # Payment Pages
    path('payment/', views.payment_page, name='payment_page'),
    path('payment/initiate/', views.initiate_payment, name='initiate_payment'),
    path('payment/confirmation/<uuid:payment_id>/', views.payment_confirmation, name='payment_confirmation'),
    path('payment/success/<uuid:payment_id>/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    
    # Payment History
    path('payment/history/', views.payment_history, name='payment_history'),
    path('payment/<uuid:payment_id>/receipt/', views.download_receipt, name='download_receipt'),
    
    # Payment Plans
    path('payment/plans/', views.payment_plans, name='payment_plans'),
    
    # M-PESA CALLBACKS
    path('payment/mpesa-callback/', views.mpesa_callback, name='mpesa_callback'),
    path('payment/mpesa-result/', views.mpesa_result, name='mpesa_result'),
    path('payment/mpesa-timeout/', views.mpesa_timeout, name='mpesa_timeout'),
    
    # PAYMENT VERIFICATION (Admin)
    path('admin/payments/verify/<uuid:payment_id>/', views.verify_payment, name='verify_payment'),
    path('admin/payments/refund/<uuid:payment_id>/', views.refund_payment, name='refund_payment'),
]