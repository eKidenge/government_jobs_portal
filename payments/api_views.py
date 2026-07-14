"""
Payments API Views
Handles API endpoints for payment processing
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
import uuid

from .models import Payment, PaymentPlan, UserPaymentAccess
from .serializers import (
    PaymentPlanSerializer,
    PaymentSerializer,
    PaymentCreateSerializer,
    PaymentStatusSerializer,
)
from accounts.models import User
from notifications.models import Notification


class PaymentPlansView(generics.ListAPIView):
    """API endpoint for getting payment plans"""
    serializer_class = PaymentPlanSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return PaymentPlan.objects.filter(is_active=True)


class InitiatePaymentView(APIView):
    """API endpoint for initiating a payment"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        plan_id = serializer.validated_data['plan_id']
        payment_method = serializer.validated_data['payment_method']
        phone_number = serializer.validated_data.get('phone_number')
        
        try:
            plan = PaymentPlan.objects.get(id=plan_id, is_active=True)
        except PaymentPlan.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Invalid payment plan selected.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
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
        
        # For M-Pesa, initiate STK push
        if payment_method == 'mpesa':
            if not phone_number:
                return Response({
                    'success': False,
                    'error': 'Phone number is required for M-Pesa payment.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Clean phone number
            phone_number = phone_number.strip()
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            elif not phone_number.startswith('254'):
                phone_number = '254' + phone_number
            
            try:
                from .mpesa import MpesaService
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
                    
                    return Response({
                        'success': True,
                        'message': 'STK Push initiated. Please check your phone.',
                        'payment_id': str(payment.id),
                        'transaction_reference': transaction_ref,
                        'checkout_request_id': response.get('CheckoutRequestID')
                    })
                else:
                    payment.status = 'failed'
                    payment.save()
                    return Response({
                        'success': False,
                        'error': f"M-Pesa error: {response.get('ResponseDescription', 'Unknown error')}"
                    }, status=status.HTTP_400_BAD_REQUEST)
                    
            except Exception as e:
                payment.status = 'failed'
                payment.save()
                return Response({
                    'success': False,
                    'error': f'Payment initiation failed: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # For other payment methods (card, bank, etc.)
        return Response({
            'success': True,
            'message': 'Payment initiated successfully',
            'payment_id': str(payment.id),
            'transaction_reference': transaction_ref
        })


class PaymentStatusView(APIView):
    """API endpoint for checking payment status"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)
        
        # For M-Pesa, check status if pending
        if payment.payment_method == 'mpesa' and payment.status == 'pending':
            try:
                from .mpesa import MpesaService
                mpesa = MpesaService()
                checkout_id = payment.metadata.get('checkout_request_id')
                
                if checkout_id:
                    response = mpesa.query_status(checkout_id)
                    
                    if response.get('ResultCode') == '0':
                        # Payment successful
                        payment.status = 'completed'
                        payment.completed_date = timezone.now()
                        payment.mpesa_receipt_number = response.get('Result', {}).get('ReceiptNumber')
                        payment.save()
                        
                        # Grant access
                        from .views import grant_payment_access
                        grant_payment_access(payment.user, payment)
                        
                        # Create notification
                        Notification.objects.create(
                            user=payment.user,
                            title='Payment Confirmed',
                            message=f'Your payment of {payment.amount} {payment.currency} has been confirmed.',
                            notification_type='payment_confirmed',
                            link='/payment/history/'
                        )
                        
                    elif response.get('ResultCode') == '2001':
                        # Still pending
                        pass
                    else:
                        payment.status = 'failed'
                        payment.save()
            except Exception as e:
                print(f"Error checking payment status: {e}")
        
        serializer = PaymentStatusSerializer(payment)
        return Response(serializer.data)


class PaymentHistoryView(generics.ListAPIView):
    """API endpoint for getting payment history"""
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(
            user=self.request.user
        ).order_by('-payment_date')


class PaymentReceiptView(APIView):
    """API endpoint for getting payment receipt"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, payment_id):
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)
        
        if payment.status != 'completed':
            return Response({
                'success': False,
                'error': 'Receipt is only available for completed payments.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': True,
            'receipt': {
                'transaction_reference': payment.transaction_reference,
                'date': payment.payment_date.strftime('%Y-%m-%d %H:%M'),
                'amount': f"{payment.currency} {payment.amount:,.2f}",
                'payment_method': payment.get_payment_method_display(),
                'status': payment.get_status_display(),
                'plan': payment.plan.name if payment.plan else 'N/A',
                'mpesa_receipt_number': payment.mpesa_receipt_number,
                'user': {
                    'name': payment.user.full_name,
                    'email': payment.user.email,
                }
            }
        })


class MpesaCallbackView(APIView):
    """API endpoint for M-Pesa callback"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        import json
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
                return Response({'ResponseCode': '00000000', 'ResponseDesc': 'Success'})
            
            if result_code == '0':
                # Payment successful
                payment.status = 'completed'
                payment.completed_date = timezone.now()
                payment.mpesa_receipt_number = result.get('Result', {}).get('ReceiptNumber')
                payment.save()
                
                # Grant access
                from .views import grant_payment_access
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
            
            return Response({'ResponseCode': '00000000', 'ResponseDesc': 'Success'})
            
        except Exception as e:
            print(f"MPesa callback error: {str(e)}")
            return Response({'ResponseCode': '00000001', 'ResponseDesc': 'Error'})


class AdminPaymentVerifyView(APIView):
    """API endpoint for admin to verify a payment"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, payment_id):
        if not request.user.is_staff:
            return Response({
                'success': False,
                'error': 'Access denied. Admin only.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        payment = get_object_or_404(Payment, id=payment_id)
        
        if payment.status != 'pending':
            return Response({
                'success': False,
                'error': 'Payment is not pending.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        payment.status = 'completed'
        payment.completed_date = timezone.now()
        payment.save()
        
        # Grant access
        from .views import grant_payment_access
        grant_payment_access(payment.user, payment)
        
        # Create notification
        Notification.objects.create(
            user=payment.user,
            title='Payment Verified',
            message=f'Your payment of {payment.amount} {payment.currency} has been verified.',
            notification_type='payment_confirmed',
            link='/payment/history/'
        )
        
        return Response({
            'success': True,
            'message': 'Payment verified successfully',
            'payment': PaymentSerializer(payment).data
        })


class AdminPaymentRefundView(APIView):
    """API endpoint for admin to refund a payment"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, payment_id):
        if not request.user.is_staff:
            return Response({
                'success': False,
                'error': 'Access denied. Admin only.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        payment = get_object_or_404(Payment, id=payment_id)
        reason = request.data.get('reason', 'No reason provided.')
        
        if payment.status != 'completed':
            return Response({
                'success': False,
                'error': 'Only completed payments can be refunded.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
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
        
        return Response({
            'success': True,
            'message': 'Payment refunded successfully',
            'payment': PaymentSerializer(payment).data
        })