"""
Payments Serializers
"""
from rest_framework import serializers
from .models import Payment, PaymentPlan, UserPaymentAccess


class PaymentPlanSerializer(serializers.ModelSerializer):
    """Serializer for Payment Plan"""
    
    class Meta:
        model = PaymentPlan
        fields = ['id', 'name', 'plan_type', 'amount', 'currency', 'description', 'is_active']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_name', 'user_email', 'plan', 'plan_name',
            'amount', 'currency', 'payment_method', 'payment_method_display',
            'transaction_reference', 'status', 'status_display',
            'mpesa_receipt_number', 'payment_date', 'completed_date',
            'subscription_start', 'subscription_end', 'metadata'
        ]
        read_only_fields = ['id', 'payment_date', 'completed_date']


class PaymentCreateSerializer(serializers.Serializer):
    """Serializer for creating a payment"""
    plan_id = serializers.UUIDField(required=True)
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_METHODS, required=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    
    def validate_plan_id(self, value):
        try:
            PaymentPlan.objects.get(id=value, is_active=True)
        except PaymentPlan.DoesNotExist:
            raise serializers.ValidationError("Invalid payment plan.")
        return value
    
    def validate(self, data):
        """Additional validation for payment method requirements"""
        payment_method = data.get('payment_method')
        phone_number = data.get('phone_number', '').strip()
        
        # For M-Pesa payments, phone number is required
        if payment_method == 'mpesa' and not phone_number:
            raise serializers.ValidationError({
                'phone_number': 'Phone number is required for M-Pesa payments.'
            })
        
        # For M-Pesa, validate phone number format (basic check)
        if payment_method == 'mpesa' and phone_number:
            # Remove any spaces or special characters
            cleaned = ''.join(filter(str.isdigit, phone_number))
            # Check if it's a valid Kenyan number (starts with 254 or 0)
            if not (cleaned.startswith('254') or cleaned.startswith('0')):
                raise serializers.ValidationError({
                    'phone_number': 'Please enter a valid Kenyan phone number.'
                })
            # Check minimum length
            if len(cleaned) < 10:
                raise serializers.ValidationError({
                    'phone_number': 'Phone number is too short. Please enter a valid number.'
                })
        
        return data


class PaymentStatusSerializer(serializers.ModelSerializer):
    """Serializer for payment status"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'transaction_reference', 'status', 'status_display',
            'amount', 'currency', 'payment_method', 'payment_date',
            'completed_date', 'mpesa_receipt_number'
        ]


class UserPaymentAccessSerializer(serializers.ModelSerializer):
    """Serializer for User Payment Access"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    has_access_display = serializers.CharField(source='get_has_access_display', read_only=True)
    
    class Meta:
        model = UserPaymentAccess
        fields = [
            'id', 'user', 'user_name', 'user_email', 'has_access',
            'access_type', 'applications_remaining', 'applications_used',
            'total_applications_allowed', 'access_start', 'access_end'
        ]