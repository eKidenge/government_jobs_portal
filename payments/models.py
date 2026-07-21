"""
Payments Models
Handles payment records, plans, and user access
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class PaymentPlan(models.Model):
    """Payment plan model"""
    PLAN_TYPES = [
        ('single', 'Single Application'),
        ('monthly', 'Monthly Access'),
        ('quarterly', 'Quarterly Access'),
        ('annual', 'Annual Access'),
        ('premium', 'Premium Access'),
    ]
    
    CURRENCY_CHOICES = [
        ('KES', 'Kenyan Shilling'),
        ('USD', 'US Dollar'),
    ]
    
    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='KES')
    description = models.TextField(blank=True)
    features = models.JSONField(default=list, blank=True)  # List of features
    duration_days = models.IntegerField(default=30, help_text="Number of days access is valid")
    is_active = models.BooleanField(default=True)
    popular = models.BooleanField(default=False)
    recommended = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['sort_order', 'amount']
        verbose_name = 'Payment Plan'
        verbose_name_plural = 'Payment Plans'
    
    def __str__(self):
        return f"{self.name} - {self.amount} {self.currency}"
    
    def get_duration_display(self):
        if self.duration_days == 30:
            return "1 Month"
        elif self.duration_days == 90:
            return "3 Months"
        elif self.duration_days == 365:
            return "1 Year"
        elif self.duration_days == 180:
            return "6 Months"
        return f"{self.duration_days} Days"


class Payment(models.Model):
    """Payment record model"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHODS = [
        ('mpesa', 'M-Pesa'),
        ('visa', 'Visa'),
        ('mastercard', 'Mastercard'),
        ('ecitizen', 'eCitizen'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    plan = models.ForeignKey(PaymentPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, choices=PaymentPlan.CURRENCY_CHOICES, default='KES')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    
    transaction_reference = models.CharField(max_length=100, unique=True, db_index=True)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, null=True)
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    
    payment_date = models.DateTimeField(default=timezone.now)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-payment_date']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['transaction_reference']),
            models.Index(fields=['payment_date']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.amount} {self.currency} - {self.status}"
    
    def is_completed(self):
        return self.status == 'completed'
    
    def is_pending(self):
        return self.status == 'pending'
    
    def is_failed(self):
        return self.status == 'failed'
    
    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)
    
    def get_payment_method_display(self):
        return dict(self.PAYMENT_METHODS).get(self.payment_method, self.payment_method)
    
    def mark_completed(self, receipt_number=None):
        self.status = 'completed'
        self.completed_date = timezone.now()
        if receipt_number:
            self.mpesa_receipt_number = receipt_number
        self.save()
    
    def mark_failed(self, error_message=None):
        self.status = 'failed'
        if error_message:
            self.metadata['error_message'] = error_message
        self.save()
    
    def mark_refunded(self):
        self.status = 'refunded'
        self.save()


class PaymentTransaction(models.Model):
    """Payment transaction log model"""
    TRANSACTION_TYPES = [
        ('initiate', 'Initiate'),
        ('complete', 'Complete'),
        ('callback', 'Callback'),
        ('query', 'Query'),
        ('verify', 'Verify'),
        ('refund', 'Refund'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('error', 'Error'),
    ]
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    request_data = models.JSONField(default=dict, blank=True)
    response_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, null=True)
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'
        indexes = [
            models.Index(fields=['payment', 'transaction_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.payment.transaction_reference} - {self.transaction_type} - {self.status}"
    
    def is_success(self):
        return self.status == 'success'


class UserPaymentAccess(models.Model):
    """User payment access model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='payment_access')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='access_grants')
    
    has_access = models.BooleanField(default=False)
    access_start_date = models.DateTimeField(null=True, blank=True)
    access_end_date = models.DateTimeField(null=True, blank=True)
    
    # Application limits
    applications_used = models.IntegerField(default=0)
    applications_limit = models.IntegerField(default=0, help_text="0 = unlimited")
    
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Payment Access'
        verbose_name_plural = 'User Payment Accesses'
        indexes = [
            models.Index(fields=['user', 'has_access']),
            models.Index(fields=['access_end_date']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {'Active' if self.has_access else 'Inactive'}"
    
    def can_apply(self):
        """Check if user can apply for jobs"""
        if not self.has_access:
            return False
        
        if self.access_end_date and self.access_end_date < timezone.now():
            self.has_access = False
            self.save()
            return False
        
        if self.applications_limit > 0 and self.applications_used >= self.applications_limit:
            return False
        
        return True
    
    def days_remaining(self):
        """Get days remaining until access expires"""
        if not self.has_access or not self.access_end_date:
            return 0
        
        delta = self.access_end_date - timezone.now()
        return max(0, delta.days)
    
    def use_application(self):
        """Increment application count"""
        if self.can_apply():
            self.applications_used += 1
            self.save()
            return True
        return False
    
    def renew_access(self, days=30):
        """Renew access for additional days"""
        if self.access_end_date and self.access_end_date > timezone.now():
            self.access_end_date = self.access_end_date + timezone.timedelta(days=days)
        else:
            self.access_end_date = timezone.now() + timezone.timedelta(days=days)
        
        self.has_access = True
        self.save()
        return self.access_end_date


class PaymentWebhook(models.Model):
    """Payment webhook log model"""
    WEBHOOK_TYPES = [
        ('mpesa_callback', 'M-Pesa Callback'),
        ('mpesa_result', 'M-Pesa Result'),
        ('mpesa_timeout', 'M-Pesa Timeout'),
        ('ecitizen', 'eCitizen'),
        ('bank', 'Bank Transfer'),
    ]
    
    webhook_type = models.CharField(max_length=20, choices=WEBHOOK_TYPES)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='webhooks')
    
    payload = models.JSONField(default=dict)
    headers = models.JSONField(default=dict, blank=True)
    
    processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True, null=True)
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment Webhook'
        verbose_name_plural = 'Payment Webhooks'
        indexes = [
            models.Index(fields=['webhook_type', 'processed']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.webhook_type} - {self.created_at}"


class Invoice(models.Model):
    """Invoice model"""
    INVOICE_STATUS = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]
    
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='draft')
    
    items = models.JSONField(default=list, blank=True)  # List of invoice items
    notes = models.TextField(blank=True, null=True)
    
    pdf_file = models.FileField(upload_to='invoices/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-issue_date']
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['user', 'status']),
        ]
    
    def __str__(self):
        return f"{self.invoice_number} - {self.user.email} - {self.total_amount}"
    
    def is_paid(self):
        return self.status == 'paid'
    
    def is_overdue(self):
        return self.status != 'paid' and self.due_date < timezone.now().date()
    
    def mark_paid(self):
        self.status = 'paid'
        self.paid_date = timezone.now().date()
        self.save()


class PaymentSettings(models.Model):
    """Payment settings model"""
    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.JSONField()
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Payment Setting'
        verbose_name_plural = 'Payment Settings'
    
    def __str__(self):
        return self.key
    
    @classmethod
    def get_setting(cls, key, default=None):
        """Get a setting value by key"""
        try:
            setting = cls.objects.get(key=key, is_active=True)
            return setting.value
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_setting(cls, key, value, description=None):
        """Set a setting value"""
        setting, created = cls.objects.get_or_create(
            key=key,
            defaults={'value': value, 'description': description}
        )
        if not created:
            setting.value = value
            if description:
                setting.description = description
            setting.save()
        return setting