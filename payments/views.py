"""
Payments Views
Handles government employment service fee payments
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings
import json
import uuid
from datetime import datetime

from .models import Payment, PaymentPlan, UserPaymentAccess
from .mpesa import MpesaService
from accounts.models import User
from jobs.models import Job, Category, Country, JobApplication
from notifications.models import Notification


@login_required
def payment_page(request):
    """Display payment options page"""
    plans = PaymentPlan.objects.filter(is_active=True)
    
    # Check if user already has access
    try:
        payment_access = UserPaymentAccess.objects.get(user=request.user)
        has_access = payment_access.has_access
    except UserPaymentAccess.DoesNotExist:
        has_access = False
    
    context = {
        'plans': plans,
        'user': request.user,
        'has_access': has_access,
    }
    return render(request, 'payments/payment_page.html', context)


@login_required
def initiate_payment(request):
    """Initiate a payment"""
    if request.method != 'POST':
        return redirect('payment_page')
    
    plan_id = request.POST.get('plan_id')
    payment_method = request.POST.get('payment_method')
    phone_number = request.POST.get('phone_number')
    
    if not plan_id:
        messages.error(request, 'Please select a payment plan.')
        return redirect('payment_page')
    
    try:
        plan = PaymentPlan.objects.get(id=plan_id, is_active=True)
    except PaymentPlan.DoesNotExist:
        messages.error(request, 'Invalid payment plan selected.')
        return redirect('payment_page')
    
    # Create payment record
    transaction_ref = f"GOVJOB-{uuid.uuid4().hex[:10].upper()}"
    
    payment = Payment.objects.create(
        user=request.user,
        plan=plan,
        amount=plan.amount,
        currency=plan.currency,
        payment_method=payment_method,
        transaction_reference=transaction_ref,
        status='pending'
    )
    
    if payment_method == 'mpesa':
        # Process M-Pesa payment
        if not phone_number:
            messages.error(request, 'Phone number is required for M-Pesa payment.')
            return redirect('payment_page')
        
        # Clean phone number
        phone_number = phone_number.strip()
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif not phone_number.startswith('254'):
            phone_number = '254' + phone_number
        
        try:
            mpesa = MpesaService()
            response = mpesa.stk_push(
                phone_number=phone_number,
                amount=str(int(plan.amount)),
                account_reference=transaction_ref,
                transaction_desc=f"Gov Jobs Fee - {plan.name}"
            )
            
            if response.get('ResponseCode') == '0':
                payment.metadata = {
                    'checkout_request_id': response.get('CheckoutRequestID'),
                    'merchant_request_id': response.get('MerchantRequestID'),
                    'phone_number': phone_number
                }
                payment.save()
                
                messages.info(request, 'Please check your phone and enter your M-Pesa PIN to complete payment.')
                return redirect('payment_confirmation', payment_id=payment.id)
            else:
                payment.status = 'failed'
                payment.save()
                messages.error(request, f"M-Pesa error: {response.get('ResponseDescription', 'Unknown error')}")
                return redirect('payment_page')
                
        except Exception as e:
            payment.status = 'failed'
            payment.save()
            messages.error(request, f'Payment initiation failed: {str(e)}')
            return redirect('payment_page')
    
    elif payment_method in ['visa', 'mastercard']:
        # Process card payment (implement with a payment gateway)
        messages.info(request, 'Card payment processing coming soon.')
        return redirect('payment_page')
    
    elif payment_method == 'ecitizen':
        # Process eCitizen payment
        messages.info(request, 'eCitizen payment processing coming soon.')
        return redirect('payment_page')
    
    elif payment_method == 'bank_transfer':
        # Process bank transfer
        messages.info(request, 'Bank transfer payment processing coming soon.')
        return redirect('payment_page')
    
    messages.error(request, 'Invalid payment method selected.')
    return redirect('payment_page')


@login_required
def payment_confirmation(request, payment_id):
    """Payment confirmation page"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    # Check if payment is already completed
    if payment.status == 'completed':
        return redirect('payment_success', payment_id=payment.id)
    
    # For M-Pesa, check status
    if payment.payment_method == 'mpesa' and payment.metadata.get('checkout_request_id'):
        try:
            mpesa = MpesaService()
            response = mpesa.query_status(payment.metadata['checkout_request_id'])
            
            if response.get('ResultCode') == '0':
                # Payment successful
                payment.status = 'completed'
                payment.completed_date = timezone.now()
                payment.mpesa_receipt_number = response.get('Result', {}).get('ReceiptNumber')
                payment.save()
                
                # Grant access
                grant_payment_access(payment.user, payment)
                
                # Create notification
                Notification.objects.create(
                    user=payment.user,
                    title='Payment Confirmed',
                    message=f'Your payment of {payment.amount} {payment.currency} has been confirmed.',
                    notification_type='payment_confirmed',
                    link='/payment/history/'
                )
                
                messages.success(request, 'Payment confirmed successfully!')
                return redirect('payment_success', payment_id=payment.id)
                
            elif response.get('ResultCode') == '2001':
                # Still pending
                messages.info(request, 'Payment is still being processed. Please wait.')
            else:
                payment.status = 'failed'
                payment.save()
                messages.error(request, f"Payment failed: {response.get('ResultDescription', 'Unknown error')}")
                return redirect('payment_page')
                
        except Exception as e:
            messages.warning(request, f'Unable to confirm payment status. Please refresh.')
    
    context = {
        'payment': payment,
    }
    return render(request, 'payments/payment_confirmation.html', context)


@login_required
def payment_success(request, payment_id):
    """Payment success page"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    if payment.status != 'completed':
        return redirect('payment_confirmation', payment_id=payment.id)
    
    context = {
        'payment': payment,
    }
    return render(request, 'payments/payment_success.html', context)


@login_required
def payment_cancel(request):
    """Payment cancellation page"""
    messages.warning(request, 'Payment was cancelled.')
    return redirect('payment_page')


@login_required
def payment_history(request):
    """View payment history"""
    payments = Payment.objects.filter(user=request.user).order_by('-payment_date')
    
    paginator = Paginator(payments, 20)
    page = request.GET.get('page')
    payments = paginator.get_page(page)
    
    context = {
        'payments': payments,
    }
    return render(request, 'payments/payment_history.html', context)


@login_required
def download_receipt(request, payment_id):
    """Download payment receipt"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    if payment.status != 'completed':
        messages.error(request, 'Receipt is only available for completed payments.')
        return redirect('payment_history')
    
    # Generate PDF receipt
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment.transaction_reference}.pdf"'
    
    # Create PDF
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    
    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1
    )
    elements.append(Paragraph('GOVERNMENT JOBS PORTAL', title_style))
    elements.append(Paragraph('Payment Receipt', styles['Heading2']))
    elements.append(Spacer(1, 20))
    
    # Receipt details
    receipt_data = [
        ['Transaction Reference:', payment.transaction_reference],
        ['Date:', payment.payment_date.strftime('%Y-%m-%d %H:%M')],
        ['Amount:', f"{payment.currency} {payment.amount:,.2f}"],
        ['Payment Method:', payment.get_payment_method_display()],
        ['Status:', payment.get_status_display()],
        ['Plan:', payment.plan.name if payment.plan else 'N/A'],
    ]
    
    if payment.mpesa_receipt_number:
        receipt_data.append(['M-Pesa Receipt:', payment.mpesa_receipt_number])
    
    table = Table(receipt_data, colWidths=[2*inch, 3*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)
    
    elements.append(Spacer(1, 30))
    elements.append(Paragraph('This is a computer-generated receipt.', styles['Normal']))
    elements.append(Paragraph('Thank you for using Government Jobs Portal.', styles['Normal']))
    
    doc.build(elements)
    return response


@login_required
def payment_plans(request):
    """Get payment plans (AJAX)"""
    plans = PaymentPlan.objects.filter(is_active=True).values(
        'id', 'name', 'plan_type', 'amount', 'currency', 'description'
    )
    return JsonResponse({'plans': list(plans)})


# ==============================================
# M-PESA CALLBACKS
# ==============================================

@csrf_exempt
def mpesa_callback(request):
    """M-Pesa callback URL handler"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            result = data.get('Body', {}).get('stkCallback', {})
            
            checkout_request_id = result.get('CheckoutRequestID')
            result_code = result.get('ResultCode')
            
            # Find payment by checkout request ID
            payment = Payment.objects.filter(
                metadata__checkout_request_id=checkout_request_id
            ).first()
            
            if not payment:
                return JsonResponse({'ResponseCode': '00000000', 'ResponseDesc': 'Success'})
            
            if result_code == '0':
                # Payment successful
                payment.status = 'completed'
                payment.completed_date = timezone.now()
                payment.mpesa_receipt_number = result.get('Result', {}).get('ReceiptNumber')
                payment.save()
                
                # Grant access
                grant_payment_access(payment.user, payment)
                
                # Create notification
                Notification.objects.create(
                    user=payment.user,
                    title='Payment Confirmed',
                    message=f'Your payment of {payment.amount} {payment.currency} has been confirmed.',
                    notification_type='payment_confirmed',
                    link='/payment/history/'
                )
            else:
                payment.status = 'failed'
                payment.save()
            
            return JsonResponse({'ResponseCode': '00000000', 'ResponseDesc': 'Success'})
            
        except Exception as e:
            print(f"MPesa callback error: {str(e)}")
            return JsonResponse({'ResponseCode': '00000001', 'ResponseDesc': 'Error'})
    
    return JsonResponse({'ResponseCode': '00000001', 'ResponseDesc': 'Invalid request'})


@csrf_exempt
def mpesa_result(request):
    """M-Pesa result URL handler"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("M-Pesa Result:", data)
            # Process result data
            return JsonResponse({'ResponseCode': '00000000', 'ResponseDesc': 'Success'})
        except Exception as e:
            print(f"MPesa result error: {str(e)}")
            return JsonResponse({'ResponseCode': '00000001', 'ResponseDesc': 'Error'})
    
    return JsonResponse({'ResponseCode': '00000001', 'ResponseDesc': 'Invalid request'})


@csrf_exempt
def mpesa_timeout(request):
    """M-Pesa timeout URL handler"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("M-Pesa Timeout:", data)
            # Process timeout data
            return JsonResponse({'ResponseCode': '00000000', 'ResponseDesc': 'Success'})
        except Exception as e:
            print(f"MPesa timeout error: {str(e)}")
            return JsonResponse({'ResponseCode': '00000001', 'ResponseDesc': 'Error'})
    
    return JsonResponse({'ResponseCode': '00000001', 'ResponseDesc': 'Invalid request'})


# ==============================================
# ADMIN PAYMENT MANAGEMENT
# ==============================================

@login_required
def verify_payment(request, payment_id):
    """Verify a payment (admin only)"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')
    
    payment = get_object_or_404(Payment, id=payment_id)
    
    if payment.status == 'pending':
        payment.status = 'completed'
        payment.completed_date = timezone.now()
        payment.save()
        
        # Grant access
        grant_payment_access(payment.user, payment)
        
        # Create notification
        Notification.objects.create(
            user=payment.user,
            title='Payment Verified',
            message=f'Your payment of {payment.amount} {payment.currency} has been verified.',
            notification_type='payment_confirmed',
            link='/payment/history/'
        )
        
        messages.success(request, f'Payment {payment.transaction_reference} verified!')
    else:
        messages.warning(request, 'Payment is not pending.')
    
    return redirect('admin_panel:admin_payment_detail', payment_id=payment_id)


@login_required
def refund_payment(request, payment_id):
    """Refund a payment (admin only)"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')
    
    payment = get_object_or_404(Payment, id=payment_id)
    reason = request.POST.get('reason', 'No reason provided.')
    
    if payment.status == 'completed':
        payment.status = 'refunded'
        payment.save()
        
        # Revoke access
        try:
            access = UserPaymentAccess.objects.get(user=payment.user)
            access.has_access = False
            access.save()
        except UserPaymentAccess.DoesNotExist:
            pass
        
        # Create notification
        Notification.objects.create(
            user=payment.user,
            title='Payment Refunded',
            message=f'Your payment of {payment.amount} {payment.currency} has been refunded. Reason: {reason}',
            notification_type='payment_refunded',
            link='/payment/history/'
        )
        
        messages.success(request, f'Payment {payment.transaction_reference} refunded!')
    else:
        messages.warning(request, 'Only completed payments can be refunded.')
    
    return redirect('admin_panel:admin_payment_detail', payment_id=payment_id)


# ==============================================
# HELPER FUNCTIONS
# ==============================================

def grant_payment_access(user, payment):
    """Grant user access to applications"""
    try:
        access = UserPaymentAccess.objects.get(user=user)
    except UserPaymentAccess.DoesNotExist:
        access = UserPaymentAccess(user=user)
    
    plan = payment.plan
    access.has_access = True
    access.access_type = plan.plan_type
    
    if plan.plan_type == 'single':
        access.total_applications_allowed = 1
        access.applications_remaining = 1
        access.access_start = timezone.now()
        access.access_end = timezone.now() + timezone.timedelta(days=30)
    elif plan.plan_type == 'monthly':
        access.total_applications_allowed = 999  # Unlimited
        access.applications_remaining = 999
        access.access_start = timezone.now()
        access.access_end = timezone.now() + timezone.timedelta(days=30)
    elif plan.plan_type == 'quarterly':
        access.total_applications_allowed = 999  # Unlimited
        access.applications_remaining = 999
        access.access_start = timezone.now()
        access.access_end = timezone.now() + timezone.timedelta(days=90)
    
    access.save()
    return access