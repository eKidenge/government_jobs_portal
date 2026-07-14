"""
Notifications App Models
Handles user notifications
"""
from django.db import models
from django.utils import timezone
import uuid
from accounts.models import User


class Notification(models.Model):
    """User Notification Model"""
    
    NOTIFICATION_TYPES = (
        ('job_approved', 'Job Approved'),
        ('job_rejected', 'Job Rejected'),
        ('application_received', 'Application Received'),
        ('application_status', 'Application Status Update'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('offer_extended', 'Offer Extended'),
        ('payment_confirmed', 'Payment Confirmed'),
        ('payment_refunded', 'Payment Refunded'),
        ('account_approved', 'Account Approved'),
        ('account_suspended', 'Account Suspended'),
        ('account_activated', 'Account Activated'),
        ('employer_verified', 'Employer Verified'),
        ('agency_verified', 'Agency Verified'),
        ('password_reset', 'Password Reset'),
        ('system', 'System Notification'),
        ('general', 'General Notification'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='general')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Optional link to related object
    link = models.CharField(max_length=200, blank=True, null=True)
    related_object_id = models.CharField(max_length=100, blank=True, null=True)
    related_object_type = models.CharField(max_length=100, blank=True, null=True)
    
    # For email/SMS notifications
    sent_via_email = models.BooleanField(default=False)
    sent_via_sms = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    sms_sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['notification_type']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} - {self.title[:50]}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at'])
    
    def mark_as_unread(self):
        """Mark notification as unread"""
        self.is_read = False
        self.read_at = None
        self.save(update_fields=['is_read', 'read_at'])
    
    @classmethod
    def create_notification(cls, user, title, message, notification_type='general', 
                           priority='medium', link=None, related_object_id=None, 
                           related_object_type=None, send_email=False, send_sms=False):
        """Create a new notification"""
        notification = cls.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            link=link,
            related_object_id=related_object_id,
            related_object_type=related_object_type,
        )
        
        # Send email if requested
        if send_email:
            notification.send_email()
        
        # Send SMS if requested
        if send_sms:
            notification.send_sms()
        
        return notification
    
    def send_email(self):
        """Send notification via email"""
        if not self.sent_via_email:
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                from django.template.loader import render_to_string
                from django.utils.html import strip_tags
                
                subject = self.title
                html_message = render_to_string('emails/notification.html', {
                    'notification': self,
                    'user': self.user,
                    'site_url': settings.SITE_URL
                })
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [self.user.email],
                    html_message=html_message,
                    fail_silently=True
                )
                
                self.sent_via_email = True
                self.email_sent_at = timezone.now()
                self.save(update_fields=['sent_via_email', 'email_sent_at'])
                
            except Exception as e:
                # Log error but don't fail
                print(f"Failed to send email notification: {e}")
    
    def send_sms(self):
        """Send notification via SMS"""
        if not self.sent_via_sms:
            try:
                # Implement SMS sending logic here
                # Example using Twilio or Africa's Talking
                # For now, just mark as sent
                self.sent_via_sms = True
                self.sms_sent_at = timezone.now()
                self.save(update_fields=['sent_via_sms', 'sms_sent_at'])
                
            except Exception as e:
                print(f"Failed to send SMS notification: {e}")


class UserNotificationPreference(models.Model):
    """User preferences for notifications"""
    
    CHANNEL_CHOICES = (
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('dashboard', 'Dashboard'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Channel preferences
    enable_email = models.BooleanField(default=True)
    enable_sms = models.BooleanField(default=False)
    enable_dashboard = models.BooleanField(default=True)
    
    # Notification type preferences
    job_approved = models.BooleanField(default=True)
    job_rejected = models.BooleanField(default=True)
    application_received = models.BooleanField(default=True)
    application_status = models.BooleanField(default=True)
    interview_scheduled = models.BooleanField(default=True)
    offer_extended = models.BooleanField(default=True)
    payment_confirmed = models.BooleanField(default=True)
    payment_refunded = models.BooleanField(default=True)
    account_approved = models.BooleanField(default=True)
    account_suspended = models.BooleanField(default=True)
    account_activated = models.BooleanField(default=True)
    system_notifications = models.BooleanField(default=True)
    general_notifications = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_notification_preferences'
    
    def __str__(self):
        return f"Preferences for {self.user.full_name}"
    
    def should_send(self, notification_type):
        """Check if notification should be sent based on preferences"""
        if notification_type == 'job_approved':
            return self.job_approved
        elif notification_type == 'job_rejected':
            return self.job_rejected
        elif notification_type == 'application_received':
            return self.application_received
        elif notification_type == 'application_status':
            return self.application_status
        elif notification_type == 'interview_scheduled':
            return self.interview_scheduled
        elif notification_type == 'offer_extended':
            return self.offer_extended
        elif notification_type == 'payment_confirmed':
            return self.payment_confirmed
        elif notification_type == 'payment_refunded':
            return self.payment_refunded
        elif notification_type == 'account_approved':
            return self.account_approved
        elif notification_type == 'account_suspended':
            return self.account_suspended
        elif notification_type == 'account_activated':
            return self.account_activated
        elif notification_type == 'system':
            return self.system_notifications
        else:
            return self.general_notifications


class NotificationLog(models.Model):
    """Audit log for notifications"""
    
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='logs')
    
    channel = models.CharField(max_length=20, choices=UserNotificationPreference.CHANNEL_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notification_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification.title} - {self.channel} - {self.status}"