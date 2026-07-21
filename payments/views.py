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
from django.core.paginator import Paginator
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.db.models import Sum, Count, Q
import json
import uuid
import logging
from datetime import datetime, timedelta

from .models import Payment, PaymentPlan, UserPaymentAccess, PaymentTransaction, PaymentWebhook, Invoice
from .mpesa import MpesaService
from accounts.models import User
from notifications.models import Notification
from jobs.models import JobApplication

logger = logging.getLogger(__name__)


# ==============================================
# PAYMENT PAGES
# ==============================================

@login_required
def payment_page(request):
    """Display payment options page"""
    plans = PaymentPlan.objects.filter(is_active=True)
    
    try:
        payment_access = UserPaymentAccess.objects.get(user=request.user)
        has_access = payment_access.has_access
        can_apply = payment_access.can_apply()
        days_remaining = payment_access.days_remaining()
    except UserPaymentAccess.DoesNotExist:
        has_access = False
        can_apply = False
        days_remaining = 0
    
    recent_payments = Payment.objects.filter(
        user=request.user
    ).order_by('-payment_date')[:5]
    
    total_paid = Payment.objects.filter(
        user=request.user,
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    context = {
        'plans': plans,
        'user': request.user,
        'has_access': has_access,
        'can_apply': can_apply,
        'days_remaining': days_remaining,
        'recent_payments': recent_payments,
        'total_paid': total_paid,
        'page_title': 'Make Payment - Government Jobs Portal',
    }
    return render(request, 'payments/payment_page.html', context)


@login_required
def initiate_payment(request):
    """Initiate a payment"""
    if request.method != 'POST':
        return redirect('payments:payment_page')
    
    plan_id = request.POST.get('plan_id')
    payment_method = request.POST.get('payment_method')
    phone_number = request.POST.get('phone_number')
    
    if not plan_id:
        messages.error(request, 'Please select a payment plan.')
        return redirect('payments:payment_page')
    
    try:
        plan = PaymentPlan.objects.get(id=plan_id, is_active=True)
    except PaymentPlan.DoesNotExist:
        messages.error(request, 'Invalid payment plan selected.')
        return redirect('payments:payment_page')
    
    valid_methods = ['mpesa', 'visa', 'mastercard', 'ecitizen', 'bank_transfer']
    if payment_method not in valid_methods:
        messages.error(request, 'Invalid payment method selected.')
        return redirect('payments:payment_page')
    
    if payment_method == 'mpesa':
        if not phone_number:
            messages.error(request, 'Phone number is required for M-Pesa payment.')
            return redirect('payments:payment_page')
        
        phone_number = phone_number.strip()
        phone_number = ''.join(filter(str.isdigit, phone_number))
        
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif phone_number.startswith('254'):
            pass
        else:
            phone_number = '254' + phone_number
        
        if len(phone_number) != 12:
            messages.error(request, 'Invalid phone number format. Use 0712345678 or 254712345678.')
            return redirect('payments:payment_page')
    
    transaction_ref = f"GOVJOB-{uuid.uuid4().hex[:10].upper()}"
    
    with transaction.atomic():
        payment = Payment.objects.create(
            user=request.user,
            plan=plan,
            amount=plan.amount,
            currency=plan.currency,
            payment_method=payment_method,
            transaction_reference=transaction_ref,
            status='pending',
            payment_date=timezone.now()
        )
    
    if payment_method == 'mpesa':
        return process_mpesa_payment(request, payment, phone_number, plan)
    
    elif payment_method in ['visa', 'mastercard']:
        messages.info(request, 'Card payment processing coming soon.')
        return redirect('payments:payment_page')
    
    elif payment_method == 'ecitizen':
        messages.info(request, 'eCitizen payment processing coming soon.')
        return redirect('payments:payment_page')
    
    elif payment_method == 'bank_transfer':
        messages.info(request, 'Please complete the bank transfer with the provided details.')
        return redirect('payments:payment_confirmation', payment_id=str(payment.id))  # FIXED: Added str()
    
    messages.error(request, 'Invalid payment method selected.')
    return redirect('payments:payment_page')


def process_mpesa_payment(request, payment, phone_number, plan):
    """Process M-Pesa payment"""
    try:
        mpesa = MpesaService()
        response = mpesa.stk_push(
            phone_number=phone_number,
            amount=str(int(plan.amount)),
            account_reference=payment.transaction_reference[:12],
            transaction_desc=f"{plan.name[:20]}"
        )
        
        if response.get('ResponseCode') == '0':
            payment.metadata = {
                'checkout_request_id': response.get('CheckoutRequestID'),
                'merchant_request_id': response.get('MerchantRequestID'),
                'phone_number': phone_number,
                'response': response
            }
            payment.save()
            
            PaymentTransaction.objects.create(
                payment=payment,
                transaction_type='initiate',
                status='pending',
                request_data=response,
                response_data=response
            )
            
            messages.info(request, 'Please check your phone and enter your M-Pesa PIN.')
            return redirect('payments:payment_confirmation', payment_id=str(payment.id))  # FIXED: Added str()
        else:
            payment.status = 'failed'
            payment.metadata = {'error': response}
            payment.save()
            error_msg = response.get('ResponseDescription', 'Unknown error')
            messages.error(request, f'M-Pesa error: {error_msg}')
            return redirect('payments:payment_page')
            
    except Exception as e:
        payment.status = 'failed'
        payment.metadata = {'error': str(e)}
        payment.save()
        logger.error(f"MPesa payment error: {str(e)}", exc_info=True)
        messages.error(request, f'Payment initiation failed: {str(e)}')
        return redirect('payments:payment_page')


@login_required
def payment_confirmation(request, payment_id):
    """Payment confirmation page"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    if payment.status == 'completed':
        return redirect('payments:payment_success', payment_id=str(payment.id))
    
    if payment.status == 'cancelled':
        messages.warning(request, 'This payment was cancelled.')
        return redirect('payments:payment_history')
    
    if payment.payment_method == 'mpesa' and payment.metadata.get('checkout_request_id'):
        try:
            mpesa = MpesaService()
            response = mpesa.query_status(payment.metadata['checkout_request_id'])
            
            if response.get('ResultCode') == '0':
                payment.status = 'completed'
                payment.completed_date = timezone.now()
                
                result = response.get('Result', {})
                receipt_number = result.get('ReceiptNumber')
                if receipt_number:
                    payment.mpesa_receipt_number = receipt_number
                
                amount = result.get('Amount')
                if amount:
                    payment.amount = amount
                
                payment.metadata = {
                    **payment.metadata,
                    'query_response': response,
                    'completed_at': timezone.now().isoformat()
                }
                payment.save()
                
                PaymentTransaction.objects.create(
                    payment=payment,
                    transaction_type='complete',
                    status='success',
                    request_data={'checkout_request_id': payment.metadata['checkout_request_id']},
                    response_data=response
                )
                
                try:
                    grant_payment_access(payment.user, payment)
                except Exception as e:
                    logger.error(f"Failed to grant access: {str(e)}")
                
                try:
                    Notification.objects.create(
                        user=payment.user,
                        title='Payment Confirmed',
                        message=f'Your payment of {payment.amount} {payment.currency} has been confirmed.',
                        notification_type='payment_confirmed',
                        link='/payment/history/'
                    )
                except Exception as e:
                    logger.error(f"Failed to create notification: {str(e)}")
                
                messages.success(request, 'Payment confirmed successfully!')
                return redirect('payments:payment_success', payment_id=str(payment.id))
                
            elif response.get('ResultCode') == '2001':
                messages.info(request, 'Payment is still being processed. Please wait or refresh.')
            else:
                payment.status = 'failed'
                payment.metadata = {
                    **payment.metadata,
                    'query_response': response,
                    'failed_at': timezone.now().isoformat()
                }
                payment.save()
                
                PaymentTransaction.objects.create(
                    payment=payment,
                    transaction_type='complete',
                    status='failed',
                    request_data={'checkout_request_id': payment.metadata['checkout_request_id']},
                    response_data=response
                )
                
                error_msg = response.get('ResultDesc', 'Unknown error')
                messages.error(request, f"Payment failed: {error_msg}")
                return redirect('payments:payment_page')
                
        except Exception as e:
            logger.error(f"Payment confirmation error: {str(e)}", exc_info=True)
            messages.warning(request, 'Unable to confirm payment status. Please refresh.')
    
    bank_details = None
    if payment.payment_method == 'bank_transfer':
        bank_details = {
            'bank_name': 'Central Bank of Kenya',
            'account_name': 'Government Jobs Portal',
            'account_number': '1234567890',
            'branch': 'Nairobi',
            'reference': payment.transaction_reference
        }
    
    context = {
        'payment': payment,
        'is_mpesa': payment.payment_method == 'mpesa',
        'is_bank_transfer': payment.payment_method == 'bank_transfer',
        'bank_details': bank_details,
        'page_title': 'Payment Confirmation - Government Jobs Portal',
    }
    return render(request, 'payments/payment_confirmation.html', context)


@login_required
def payment_success(request, payment_id):
    """Payment success page"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    if payment.status != 'completed':
        return redirect('payments:payment_confirmation', payment_id=str(payment.id))
    
    try:
        access = UserPaymentAccess.objects.get(user=request.user)
        has_access = access.has_access
        days_remaining = access.days_remaining()
    except UserPaymentAccess.DoesNotExist:
        has_access = False
        days_remaining = 0
    
    context = {
        'payment': payment,
        'has_access': has_access,
        'days_remaining': days_remaining,
        'page_title': 'Payment Successful - Government Jobs Portal',
    }
    return render(request, 'payments/payment_success.html', context)


@login_required
def payment_cancel(request):
    """Payment cancellation page"""
    messages.warning(request, 'Payment was cancelled.')
    return redirect('payments:payment_page')


# ==============================================
# PAYMENT HISTORY & RECEIPTS
# ==============================================

@login_required
def payment_history(request):
    """View payment history"""
    payments = Payment.objects.filter(user=request.user).order_by('-payment_date')
    
    completed_count = payments.filter(status='completed').count()
    pending_count = payments.filter(status='pending').count()
    failed_count = payments.filter(status='failed').count()
    
    total_spent = payments.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
    
    status_filter = request.GET.get('status')
    if status_filter and status_filter in ['completed', 'pending', 'failed', 'cancelled']:
        payments = payments.filter(status=status_filter)
    
    paginator = Paginator(payments, 20)
    page = request.GET.get('page')
    payments_page = paginator.get_page(page)
    
    context = {
        'payments': payments_page,
        'completed_count': completed_count,
        'pending_count': pending_count,
        'failed_count': failed_count,
        'total_spent': total_spent,
        'current_filter': status_filter,
        'page_title': 'Payment History - Government Jobs Portal',
    }
    return render(request, 'payments/payment_history.html', context)


@login_required
def download_receipt(request, payment_id):
    """Download payment receipt as PDF"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    if payment.status != 'completed':
        messages.error(request, 'Receipt is only available for completed payments.')
        return redirect('payments:payment_history')
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="receipt_{payment.transaction_reference}.pdf"'
    
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_CENTER
        
        doc = SimpleDocTemplate(response, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1a237e')
        )
        
        elements.append(Paragraph('GOVERNMENT JOBS PORTAL', title_style))
        elements.append(Paragraph('Official Payment Receipt', styles['Heading2']))
        elements.append(Spacer(1, 20))
        
        receipt_header_data = [
            ['Receipt Number:', payment.transaction_reference],
            ['Date:', payment.payment_date.strftime('%Y-%m-%d %H:%M:%S')],
            ['Status:', 'PAID'],
        ]
        
        header_table = Table(receipt_header_data, colWidths=[3*inch, 4*inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8eaf6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#1a237e')),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 20))
        
        payment_details = [
            ['Amount:', f"{payment.currency} {payment.amount:,.2f}"],
            ['Payment Method:', payment.get_payment_method_display()],
            ['Plan:', payment.plan.name if payment.plan else 'N/A'],
        ]
        
        if payment.mpesa_receipt_number:
            payment_details.append(['M-Pesa Receipt:', payment.mpesa_receipt_number])
        
        details_table = Table(payment_details, colWidths=[2.5*inch, 4.5*inch])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdbdbd')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(details_table)
        elements.append(Spacer(1, 30))
        
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#757575')
        )
        elements.append(Paragraph('This is a computer-generated receipt. No signature required.', footer_style))
        elements.append(Paragraph(f'Generated on: {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}', footer_style))
        elements.append(Paragraph('Thank you for using Government Jobs Portal.', footer_style))
        
        doc.build(elements)
        
    except ImportError:
        content = f"""
        GOVERNMENT JOBS PORTAL
        Official Payment Receipt
        
        Receipt Number: {payment.transaction_reference}
        Date: {payment.payment_date.strftime('%Y-%m-%d %H:%M:%S')}
        Status: PAID
        
        Amount: {payment.currency} {payment.amount:,.2f}
        Payment Method: {payment.get_payment_method_display()}
        Plan: {payment.plan.name if payment.plan else 'N/A'}
        """
        if payment.mpesa_receipt_number:
            content += f"\nM-Pesa Receipt: {payment.mpesa_receipt_number}"
        
        response.content = content
    
    return response


@login_required
def view_receipt(request, payment_id):
    """View payment receipt online (HTML version)"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    if payment.status != 'completed':
        messages.error(request, 'Receipt is only available for completed payments.')
        return redirect('payments:payment_history')
    
    context = {
        'payment': payment,
        'page_title': 'Payment Receipt - Government Jobs Portal',
    }
    return render(request, 'payments/payment_receipt.html', context)


# ==============================================
# PAYMENT PLANS (AJAX)
# ==============================================

@login_required
def payment_plans(request):
    """Get payment plans (AJAX)"""
    plans = PaymentPlan.objects.filter(is_active=True).values(
        'id', 'name', 'plan_type', 'amount', 'currency', 'description', 
        'features', 'popular', 'recommended'
    )
    return JsonResponse({
        'success': True,
        'plans': list(plans)
    })


# ==============================================
# PAYMENT STATUS (AJAX)
# ==============================================

@login_required
@require_GET
def check_payment_status(request, payment_id):
    """Check payment status via AJAX"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    if payment.payment_method == 'mpesa' and payment.metadata.get('checkout_request_id'):
        try:
            mpesa = MpesaService()
            response = mpesa.query_status(payment.metadata['checkout_request_id'])
            
            if response.get('ResultCode') == '0':
                payment.status = 'completed'
                payment.completed_date = timezone.now()
                payment.mpesa_receipt_number = response.get('Result', {}).get('ReceiptNumber')
                payment.save()
                grant_payment_access(payment.user, payment)
                return JsonResponse({
                    'success': True,
                    'status': 'completed',
                    'message': 'Payment confirmed!',
                    'receipt_number': payment.mpesa_receipt_number
                })
            elif response.get('ResultCode') == '2001':
                return JsonResponse({
                    'success': True,
                    'status': 'pending',
                    'message': 'Payment is still processing...'
                })
            else:
                payment.status = 'failed'
                payment.save()
                return JsonResponse({
                    'success': False,
                    'status': 'failed',
                    'message': 'Payment failed'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'success': True,
        'status': payment.status,
        'message': f'Payment is {payment.get_status_display()}'
    })


# ==============================================
# ACCESS CHECK
# ==============================================

@login_required
def check_access(request):
    """Check if user has access and can apply (AJAX)"""
    try:
        access = UserPaymentAccess.objects.get(user=request.user)
        has_access = access.has_access
        can_apply = access.can_apply()
        days_remaining = access.days_remaining()
        expiry_date = access.access_end_date
    except UserPaymentAccess.DoesNotExist:
        has_access = False
        can_apply = False
        days_remaining = 0
        expiry_date = None
    
    return JsonResponse({
        'has_access': has_access,
        'can_apply': can_apply,
        'days_remaining': days_remaining,
        'expiry_date': expiry_date.isoformat() if expiry_date else None,
    })


# ==============================================
# M-PESA CALLBACKS
# ==============================================

@csrf_exempt
def mpesa_callback(request):
    """M-Pesa callback URL handler"""
    if request.method != 'POST':
        return JsonResponse({'ResponseCode': '00000001', 'ResponseDesc': 'Invalid request'})
    
    try:
        data = json.loads(request.body)
        logger.info(f"M-Pesa callback received: {json.dumps(data)}")
        
        stk_callback = data.get('Body', {}).get('stkCallback', {})
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        result_code = stk_callback.get('ResultCode')
        result_desc = stk_callback.get('ResultDesc')
        callback_metadata = stk_callback.get('CallbackMetadata', {})
        
        if not checkout_request_id:
            logger.error("No CheckoutRequestID in callback")
            return JsonResponse({'ResponseCode': '00000001', 'ResponseDesc': 'Missing CheckoutRequestID'})
        
        payment = Payment.objects.filter(
            metadata__checkout_request_id=checkout_request_id
        ).first()
        
        if not payment:
            logger.warning(f"Payment not found for CheckoutRequestID: {checkout_request_id}")
            return JsonResponse({'ResponseCode': '00000000', 'ResponseDesc': 'Success'})
        
        if payment.status == 'completed':
            logger.info(f"Payment already completed: {checkout_request_id}")
            return JsonResponse({'ResponseCode': '00000000', 'ResponseDesc': 'Success'})
        
        if result_code == '0':
            payment.status = 'completed'
            payment.completed_date = timezone.now()
            
            items = callback_metadata.get('Item', [])
            receipt_number = None
            amount = None
            
            for item in items:
                name = item.get('Name')
                value = item.get('Value')
                if name == 'ReceiptNumber':
                    receipt_number = value
                elif name == 'Amount':
                    amount = value
            
            payment.mpesa_receipt_number = receipt_number
            if amount:
                payment.amount = amount
            
            payment.metadata = {
                **payment.metadata,
                'callback_data': data,
                'callback_receipt': receipt_number,
                'callback_amount': amount,
                'completed_at': timezone.now().isoformat()
            }
            payment.save()
            
            PaymentTransaction.objects.create(
                payment=payment,
                transaction_type='callback',
                status='success',
                request_data={'checkout_request_id': checkout_request_id},
                response_data=data
            )
            
            try:
                grant_payment_access(payment.user, payment)
                logger.info(f"Access granted to {payment.user.email}")
            except Exception as e:
                logger.error(f"Failed to grant access: {str(e)}")
            
            try:
                Notification.objects.create(
                    user=payment.user,
                    title='Payment Confirmed',
                    message=f'Your payment of {payment.amount} {payment.currency} has been confirmed.',
                    notification_type='payment_confirmed',
                    link='/payment/history/',
                    is_read=False
                )
            except Exception as e:
                logger.error(f"Failed to create notification: {str(e)}")
            
            logger.info(f"Payment completed: {payment.transaction_reference}")
            
        else:
            payment.status = 'failed'
            payment.metadata = {
                **payment.metadata,
                'callback_data': data,
                'callback_error_code': result_code,
                'callback_error_description': result_desc,
                'failed_at': timezone.now().isoformat()
            }
            payment.save()
            
            PaymentTransaction.objects.create(
                payment=payment,
                transaction_type='callback',
                status='failed',
                request_data={'checkout_request_id': checkout_request_id},
                response_data=data
            )
            
            try:
                Notification.objects.create(
                    user=payment.user,
                    title='Payment Failed',
                    message=f'Your payment failed. Error: {result_desc}',
                    notification_type='payment_failed',
                    link='/payment/',
                    is_read=False
                )
            except Exception as e:
                logger.error(f"Failed to create notification: {str(e)}")
            
            logger.info(f"Payment failed: {result_desc}")
        
        return JsonResponse({'ResponseCode': '00000000', 'ResponseDesc': 'Success'})
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in callback: {str(e)}")
        return JsonResponse({'ResponseCode': '00000001', 'ResponseDesc': 'Invalid JSON'})
    except Exception as e:
        logger.error(f"MPesa callback error: {str(e)}", exc_info=True)
        return JsonResponse({'ResponseCode': '00000001', 'ResponseDesc': 'Internal error'})


@csrf_exempt
def mpesa_result(request):
    """M-Pesa result URL handler"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info(f"M-Pesa Result received: {json.dumps(data)}")
            return JsonResponse({'ResponseCode': '00000000', 'ResponseDesc': 'Success'})
        except Exception as e:
            logger.error(f"MPesa result error: {str(e)}")
            return JsonResponse({'ResponseCode': '00000001', 'ResponseDesc': 'Error'})
    
    return JsonResponse({'ResponseCode': '00000001', 'ResponseDesc': 'Invalid request'})


@csrf_exempt
def mpesa_timeout(request):
    """M-Pesa timeout URL handler"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info(f"M-Pesa Timeout received: {json.dumps(data)}")
            
            checkout_request_id = data.get('CheckoutRequestID')
            if checkout_request_id:
                payment = Payment.objects.filter(
                    metadata__checkout_request_id=checkout_request_id
                ).first()
                
                if payment and payment.status == 'pending':
                    payment.status = 'failed'
                    payment.metadata = {
                        **payment.metadata,
                        'timeout_data': data,
                        'timeout_at': timezone.now().isoformat()
                    }
                    payment.save()
                    logger.warning(f"Payment timeout for {checkout_request_id}")
            
            return JsonResponse({'ResponseCode': '00000000', 'ResponseDesc': 'Success'})
        except Exception as e:
            logger.error(f"MPesa timeout error: {str(e)}")
            return JsonResponse({'ResponseCode': '00000001', 'ResponseDesc': 'Error'})
    
    return JsonResponse({'ResponseCode': '00000001', 'ResponseDesc': 'Invalid request'})


# ==============================================
# WEBHOOKS
# ==============================================

@csrf_exempt
def mpesa_webhook(request):
    """M-Pesa webhook endpoint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info(f"M-Pesa webhook received: {json.dumps(data)}")
            
            webhook = PaymentWebhook.objects.create(
                webhook_type='mpesa_callback',
                payload=data,
                headers=dict(request.headers),
                ip_address=request.META.get('REMOTE_ADDR'),
                processed=False
            )
            
            stk_callback = data.get('Body', {}).get('stkCallback', {})
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            
            if checkout_request_id:
                payment = Payment.objects.filter(
                    metadata__checkout_request_id=checkout_request_id
                ).first()
                
                if payment:
                    webhook.payment = payment
                    
                    if stk_callback.get('ResultCode') == '0':
                        payment.status = 'completed'
                        payment.completed_date = timezone.now()
                        payment.save()
                        grant_payment_access(payment.user, payment)
                    
                    webhook.processed = True
                    webhook.processed_at = timezone.now()
                    webhook.save()
            
            return JsonResponse({'status': 'ok'}, status=200)
        except Exception as e:
            logger.error(f"MPesa webhook error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'method not allowed'}, status=405)


@csrf_exempt
def ecitizen_webhook(request):
    """eCitizen webhook endpoint"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.info(f"eCitizen webhook received: {json.dumps(data)}")
            
            webhook = PaymentWebhook.objects.create(
                webhook_type='ecitizen',
                payload=data,
                headers=dict(request.headers),
                ip_address=request.META.get('REMOTE_ADDR'),
                processed=True,
                processed_at=timezone.now()
            )
            
            return JsonResponse({'status': 'ok'}, status=200)
        except Exception as e:
            logger.error(f"eCitizen webhook error: {str(e)}")
            return JsonResponse({'status': 'error'}, status=500)
    
    return JsonResponse({'status': 'method not allowed'}, status=405)


# ==============================================
# INVOICES
# ==============================================

@login_required
def generate_invoice(request, payment_id):
    """Generate invoice for a payment"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    if payment.status != 'completed':
        messages.error(request, 'Invoice is only available for completed payments.')
        return redirect('payments:payment_history')
    
    invoice = Invoice.objects.filter(payment=payment).first()
    
    if not invoice:
        invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
        
        invoice = Invoice.objects.create(
            invoice_number=invoice_number,
            payment=payment,
            user=payment.user,
            amount=payment.amount,
            tax=0,
            total_amount=payment.amount,
            issue_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=30),
            status='paid' if payment.status == 'completed' else 'sent',
            items=[
                {
                    'description': payment.plan.name if payment.plan else 'Payment',
                    'amount': float(payment.amount),
                    'currency': payment.currency
                }
            ]
        )
    
    context = {
        'invoice': invoice,
        'payment': payment,
        'page_title': 'Invoice - Government Jobs Portal',
    }
    return render(request, 'payments/invoice.html', context)


@login_required
def download_invoice(request, payment_id):
    """Download invoice as PDF"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    invoice = get_object_or_404(Invoice, payment=payment)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_number}.pdf"'
    
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT
        
        doc = SimpleDocTemplate(response, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1a237e')
        )
        elements.append(Paragraph('GOVERNMENT JOBS PORTAL', title_style))
        elements.append(Paragraph('INVOICE', styles['Heading2']))
        elements.append(Spacer(1, 20))
        
        invoice_data = [
            ['Invoice Number:', invoice.invoice_number],
            ['Date:', invoice.issue_date.strftime('%Y-%m-%d')],
            ['Due Date:', invoice.due_date.strftime('%Y-%m-%d')],
            ['Status:', invoice.get_status_display()],
        ]
        
        table = Table(invoice_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f5f5f5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdbdbd')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        amount_data = [
            ['Amount:', f"{payment.currency} {payment.amount:,.2f}"],
        ]
        amount_table = Table(amount_data, colWidths=[2*inch, 4*inch])
        amount_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f5e9')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#4caf50')),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(amount_table)
        elements.append(Spacer(1, 30))
        
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#757575')
        )
        elements.append(Paragraph('Thank you for using Government Jobs Portal.', footer_style))
        
        doc.build(elements)
    except ImportError:
        content = f"""
        GOVERNMENT JOBS PORTAL        INVOICE
        
        Invoice Number: {invoice.invoice_number}
        Date: {invoice.issue_date.strftime('%Y-%m-%d')}
        Due Date: {invoice.due_date.strftime('%Y-%m-%d')}
        Status: {invoice.get_status_display()}
        
        Amount: {payment.currency} {payment.amount:,.2f}
        
        Thank you for using Government Jobs Portal.
        """
        response.content = content
    
    return response


# ==============================================
# SUBSCRIPTION MANAGEMENT
# ==============================================

@login_required
def manage_subscription(request):
    """Manage user subscription"""
    try:
        access = UserPaymentAccess.objects.get(user=request.user)
        has_access = access.has_access
        days_remaining = access.days_remaining()
        expiry_date = access.access_end_date
    except UserPaymentAccess.DoesNotExist:
        has_access = False
        days_remaining = 0
        expiry_date = None
    
    plans = PaymentPlan.objects.filter(is_active=True)
    
    context = {
        'has_access': has_access,
        'days_remaining': days_remaining,
        'expiry_date': expiry_date,
        'plans': plans,
        'page_title': 'Manage Subscription - Government Jobs Portal',
    }
    return render(request, 'payments/manage_subscription.html', context)


@login_required
@require_POST
def cancel_subscription(request):
    """Cancel user subscription"""
    try:
        access = UserPaymentAccess.objects.get(user=request.user)
        access.has_access = False
        access.save()
        
        Notification.objects.create(
            user=request.user,
            title='Subscription Cancelled',
            message='Your subscription has been cancelled successfully.',
            notification_type='subscription_cancelled',
            link='/payment/',
            is_read=False
        )
        
        messages.success(request, 'Your subscription has been cancelled.')
    except UserPaymentAccess.DoesNotExist:
        messages.error(request, 'No active subscription found.')
    
    return redirect('payments:manage_subscription')


@login_required
def renew_subscription(request):
    """Renew subscription - redirect to payment page"""
    messages.info(request, 'Please select a plan to renew your subscription.')
    return redirect('payments:payment_page')


# ==============================================
# ADMIN VIEWS
# ==============================================

@staff_member_required
def admin_payments(request):
    """Admin view for all payments"""
    payments = Payment.objects.all().order_by('-payment_date')
    
    status = request.GET.get('status')
    if status:
        payments = payments.filter(status=status)
    
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        payments = payments.filter(payment_date__gte=date_from)
    if date_to:
        payments = payments.filter(payment_date__lte=date_to)
    
    search = request.GET.get('search')
    if search:
        payments = payments.filter(
            Q(transaction_reference__icontains=search) |
            Q(user__email__icontains=search) |
            Q(user__username__icontains=search)
        )
    
    total_payments = Payment.objects.count()
    total_completed = Payment.objects.filter(status='completed').count()
    total_amount = Payment.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
    pending_payments = Payment.objects.filter(status='pending').count()
    
    paginator = Paginator(payments, 50)
    page = request.GET.get('page')
    payments_page = paginator.get_page(page)
    
    context = {
        'payments': payments_page,
        'total_payments': total_payments,
        'total_completed': total_completed,
        'total_amount': total_amount,
        'pending_payments': pending_payments,
        'current_status': status,
        'date_from': date_from,
        'date_to': date_to,
        'search': search,
        'page_title': 'Admin - Payment Management',
    }
    return render(request, 'payments/admin_payments.html', context)


@staff_member_required
def admin_payment_detail(request, payment_id):
    """Admin view for payment detail"""
    payment = get_object_or_404(Payment, id=payment_id)
    transactions = PaymentTransaction.objects.filter(payment=payment).order_by('-created_at')
    
    context = {
        'payment': payment,
        'transactions': transactions,
        'page_title': f'Payment Detail - {payment.transaction_reference}',
    }
    return render(request, 'payments/admin_payment_detail.html', context)


@staff_member_required
@require_POST
def admin_refund_payment(request, payment_id):
    """Admin refund a payment"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if payment.status != 'completed':
        messages.error(request, 'Only completed payments can be refunded.')
        return redirect('payments:admin_payment_detail', payment_id=payment.id)
    
    try:
        payment.status = 'refunded'
        payment.metadata = {
            **payment.metadata,
            'refunded_at': timezone.now().isoformat(),
            'refunded_by': request.user.email
        }
        payment.save()
        
        try:
            access = UserPaymentAccess.objects.get(user=payment.user)
            access.has_access = False
            access.save()
        except UserPaymentAccess.DoesNotExist:
            pass
        
        Notification.objects.create(
            user=payment.user,
            title='Payment Refunded',
            message=f'Your payment of {payment.amount} {payment.currency} has been refunded.',
            notification_type='payment_refunded',
            link='/payment/history/',
            is_read=False
        )
        
        messages.success(request, f'Payment {payment.transaction_reference} refunded successfully.')
    except Exception as e:
        logger.error(f"Refund error: {str(e)}")
        messages.error(request, f'Failed to refund payment: {str(e)}')
    
    return redirect('payments:admin_payment_detail', payment_id=payment.id)


@staff_member_required
@require_POST
def admin_verify_payment(request, payment_id):
    """Admin verify a payment manually"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if payment.status != 'pending':
        messages.error(request, 'Only pending payments can be verified.')
        return redirect('payments:admin_payment_detail', payment_id=payment.id)
    
    try:
        payment.status = 'completed'
        payment.completed_date = timezone.now()
        payment.metadata = {
            **payment.metadata,
            'verified_by': request.user.email,
            'verified_at': timezone.now().isoformat(),
            'manual_verification': True
        }
        payment.save()
        
        grant_payment_access(payment.user, payment)
        
        Notification.objects.create(
            user=payment.user,
            title='Payment Verified',
            message=f'Your payment of {payment.amount} {payment.currency} has been manually verified.',
            notification_type='payment_verified',
            link='/payment/history/',
            is_read=False
        )
        
        messages.success(request, f'Payment {payment.transaction_reference} verified successfully.')
    except Exception as e:
        logger.error(f"Verification error: {str(e)}")
        messages.error(request, f'Failed to verify payment: {str(e)}')
    
    return redirect('payments:admin_payment_detail', payment_id=payment.id)


@staff_member_required
def payment_reports(request):
    """Payment reports view"""
    payments = Payment.objects.all()
    
    total_payments = payments.count()
    total_completed = payments.filter(status='completed').count()
    total_amount = payments.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
    
    monthly_data = payments.filter(
        status='completed',
        payment_date__year=timezone.now().year
    ).values('payment_date__month').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('payment_date__month')
    
    context = {
        'total_payments': total_payments,
        'total_completed': total_completed,
        'total_amount': total_amount,
        'monthly_data': monthly_data,
        'page_title': 'Payment Reports - Admin',
    }
    return render(request, 'payments/admin_reports.html', context)


@staff_member_required
def export_payments(request):
    """Export payments as CSV"""
    import csv
    from io import StringIO
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payments_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Transaction Reference', 'User', 'Email', 'Amount', 'Currency',
        'Payment Method', 'Status', 'Date', 'Receipt Number'
    ])
    
    payments = Payment.objects.all().order_by('-payment_date')
    for payment in payments:
        writer.writerow([
            payment.transaction_reference,
            payment.user.username,
            payment.user.email,
            payment.amount,
            payment.currency,
            payment.get_payment_method_display(),
            payment.get_status_display(),
            payment.payment_date.strftime('%Y-%m-%d %H:%M:%S'),
            payment.mpesa_receipt_number or ''
        ])
    
    return response


@staff_member_required
def revenue_report(request):
    """Revenue report view"""
    payments = Payment.objects.filter(status='completed')
    
    total_revenue = payments.aggregate(total=Sum('amount'))['total'] or 0
    
    revenue_by_plan = payments.values('plan__name').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    revenue_by_month = payments.values('payment_date__year', 'payment_date__month').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('payment_date__year', 'payment_date__month')
    
    context = {
        'total_revenue': total_revenue,
        'revenue_by_plan': revenue_by_plan,
        'revenue_by_month': revenue_by_month,
        'page_title': 'Revenue Report - Admin',
    }
    return render(request, 'payments/admin_revenue.html', context)


# ==============================================
# API ENDPOINTS (REST API)
# ==============================================

@csrf_exempt
def api_initiate_payment(request):
    """API endpoint to initiate payment"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        user = request.user if request.user.is_authenticated else None
        
        phone_number = data.get('phone_number')
        plan_id = data.get('plan_id')
        
        if not phone_number or not plan_id:
            return JsonResponse({'error': 'phone_number and plan_id are required'}, status=400)
        
        plan = get_object_or_404(PaymentPlan, id=plan_id, is_active=True)
        
        phone_number = ''.join(filter(str.isdigit, phone_number))
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif not phone_number.startswith('254'):
            phone_number = '254' + phone_number
        
        transaction_ref = f"API-{uuid.uuid4().hex[:8].upper()}"
        
        payment = Payment.objects.create(
            user=user,
            plan=plan,
            amount=plan.amount,
            currency=plan.currency,
            payment_method='mpesa',
            transaction_reference=transaction_ref,
            status='pending',
            payment_date=timezone.now()
        )
        
        mpesa = MpesaService()
        response = mpesa.stk_push(
            phone_number=phone_number,
            amount=str(int(plan.amount)),
            account_reference=transaction_ref[:12],
            transaction_desc=f"{plan.name[:20]}"
        )
        
        if response.get('ResponseCode') == '0':
            payment.metadata = {
                'checkout_request_id': response.get('CheckoutRequestID'),
                'phone_number': phone_number
            }
            payment.save()
            
            return JsonResponse({
                'success': True,
                'checkout_request_id': response.get('CheckoutRequestID'),
                'transaction_reference': transaction_ref
            })
        else:
            payment.status = 'failed'
            payment.save()
            return JsonResponse({
                'success': False,
                'error': response.get('ResponseDescription', 'Unknown error')
            }, status=400)
            
    except Exception as e:
        logger.error(f"API payment error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_payment_status(request, payment_id):
    """API endpoint to check payment status"""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    return JsonResponse({
        'status': payment.status,
        'amount': float(payment.amount),
        'currency': payment.currency,
        'transaction_reference': payment.transaction_reference,
        'payment_date': payment.payment_date.isoformat(),
        'completed_date': payment.completed_date.isoformat() if payment.completed_date else None,
        'receipt_number': payment.mpesa_receipt_number
    })


@login_required
def api_payment_history(request):
    """API endpoint to get payment history"""
    payments = Payment.objects.filter(user=request.user).order_by('-payment_date')
    
    data = []
    for payment in payments:
        data.append({
            'id': str(payment.id),  # FIXED: Convert UUID to string
            'amount': float(payment.amount),
            'currency': payment.currency,
            'payment_method': payment.get_payment_method_display(),
            'status': payment.status,
            'transaction_reference': payment.transaction_reference,
            'payment_date': payment.payment_date.isoformat(),
            'receipt_number': payment.mpesa_receipt_number
        })
    
    return JsonResponse({
        'payments': data,
        'count': len(data)
    })


@staff_member_required
def api_verify_payment(request, payment_id):
    """API endpoint to verify payment (admin)"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if payment.status != 'pending':
        return JsonResponse({'error': 'Payment is not pending'}, status=400)
    
    try:
        payment.status = 'completed'
        payment.completed_date = timezone.now()
        payment.metadata = {
            **payment.metadata,
            'verified_by_api': request.user.email,
            'verified_at_api': timezone.now().isoformat()
        }
        payment.save()
        
        grant_payment_access(payment.user, payment)
        
        return JsonResponse({
            'success': True,
            'status': payment.status,
            'transaction_reference': payment.transaction_reference
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ==============================================
# TEST ENDPOINTS (Development Only)
# ==============================================

def test_mpesa(request):
    """Test M-Pesa integration"""
    if settings.DEBUG:
        return render(request, 'payments/test_mpesa.html')
    return redirect('payments:payment_page')


def test_success(request):
    """Test success page"""
    if settings.DEBUG:
        return render(request, 'payments/test_success.html')
    return redirect('payments:payment_page')


def test_failure(request):
    """Test failure page"""
    if settings.DEBUG:
        return render(request, 'payments/test_failure.html')
    return redirect('payments:payment_page')


# ==============================================
# HELPER FUNCTIONS
# ==============================================

def grant_payment_access(user, payment):
    """Grant access to user after payment"""
    try:
        access, created = UserPaymentAccess.objects.get_or_create(
            user=user,
            defaults={
                'has_access': True,
                'access_start_date': timezone.now()
            }
        )
        
        if payment.plan:
            plan_durations = {
                'single': 30,
                'monthly': 30,
                'quarterly': 90,
                'annual': 365,
                'premium': 180
            }
            days = plan_durations.get(payment.plan.plan_type, 30)
            access.access_end_date = timezone.now() + timedelta(days=days)
        
        if access.access_end_date and access.access_end_date < timezone.now():
            access.access_end_date = timezone.now() + timedelta(days=30)
        
        access.has_access = True
        access.payment = payment
        access.save()
        
        logger.info(f"Access granted to {user.email} until {access.access_end_date}")
        return access
        
    except Exception as e:
        logger.error(f"Error granting access: {str(e)}")
        raise


def get_phone_number_from_request(request):
    """Extract and format phone number from request"""
    phone = request.POST.get('phone_number', '').strip()
    phone = ''.join(filter(str.isdigit, phone))
    
    if phone.startswith('0'):
        phone = '254' + phone[1:]
    elif phone.startswith('+254'):
        phone = phone[1:]
    elif len(phone) == 9 and phone.startswith('7'):
        phone = '254' + phone
    elif not phone.startswith('254'):
        phone = '254' + phone
    
    return phone if len(phone) == 12 else None