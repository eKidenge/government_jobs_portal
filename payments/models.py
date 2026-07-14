from django.db import models
import uuid
from accounts.models import User

class PaymentPlan(models.Model):
    PLAN_TYPES = (
        ('single', 'Single Application'),
        ('monthly', 'Monthly Access'),
        ('quarterly', 'Quarterly Access'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='KES')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_plans'
    
    def __str__(self):
        return f"{self.name} - {self.amount} {self.currency}"

class Payment(models.Model):
    PAYMENT_METHODS = (
        ('ecitizen', 'eCitizen'),
        ('mpesa', 'M-Pesa'),
        ('bank_transfer', 'Bank Transfer'),
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(PaymentPlan, on_delete=models.SET_NULL, null=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='KES')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # M-Pesa specific
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, null=True)
    mpesa_phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    # Bank Transfer specific
    bank_reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Payment metadata
    metadata = models.JSONField(default=dict, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateTimeField(blank=True, null=True)
    
    # For subscription tracking
    subscription_start = models.DateTimeField(blank=True, null=True)
    subscription_end = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payments'
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['transaction_reference']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} - {self.amount} {self.currency}"
    
    def is_completed(self):
        return self.status == 'completed'

class UserPaymentAccess(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='payment_access')
    
    has_access = models.BooleanField(default=False)
    access_type = models.CharField(max_length=20, blank=True, null=True)  # single, monthly, quarterly
    applications_remaining = models.IntegerField(default=0)  # For single plan
    
    # Access period
    access_start = models.DateTimeField(blank=True, null=True)
    access_end = models.DateTimeField(blank=True, null=True)
    
    # Total applications allowed based on plan
    total_applications_allowed = models.IntegerField(default=0)
    applications_used = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_payment_access'
    
    def __str__(self):
        return f"{self.user.full_name} - {'Active' if self.has_access else 'Inactive'}"
    
    def can_apply(self):
        if not self.has_access:
            return False
        if self.access_type == 'single':
            return self.applications_used < self.total_applications_allowed
        if self.access_type in ['monthly', 'quarterly']:
            return timezone.now() <= self.access_end
        return False