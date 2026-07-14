"""
Admin Panel Models
For system settings and audit logs
"""
from django.db import models
from django.utils import timezone
import uuid
from accounts.models import User


class SystemSetting(models.Model):
    """System settings configuration"""
    
    SETTING_TYPES = (
        ('string', 'String'),
        ('integer', 'Integer'),
        ('decimal', 'Decimal'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    value_type = models.CharField(max_length=20, choices=SETTING_TYPES, default='string')
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_settings'
        ordering = ['key']
    
    def __str__(self):
        return self.key
    
    def get_value(self):
        """Get typed value"""
        if self.value_type == 'integer':
            return int(self.value)
        elif self.value_type == 'decimal':
            return float(self.value)
        elif self.value_type == 'boolean':
            return self.value.lower() in ('true', '1', 'yes')
        elif self.value_type == 'json':
            import json
            return json.loads(self.value)
        return self.value


class AdminActionLog(models.Model):
    """Audit log for admin actions"""
    
    ACTION_TYPES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('suspend', 'Suspend'),
        ('activate', 'Activate'),
        ('verify', 'Verify'),
        ('refund', 'Refund'),
        ('export', 'Export'),
        ('import', 'Import'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='admin_actions')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    object_repr = models.CharField(max_length=200)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'admin_action_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['admin', 'action_type']),
            models.Index(fields=['model_name', 'object_id']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.admin.full_name} - {self.action_type} - {self.model_name}"


class AdminNotification(models.Model):
    """Admin notifications"""
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=200, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'admin_notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def mark_as_read(self):
        self.is_read = True
        self.read_at = timezone.now()
        self.save()