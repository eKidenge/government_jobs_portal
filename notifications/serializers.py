"""
Notifications Serializers
"""
from rest_framework import serializers
from .models import Notification, UserNotificationPreference, NotificationLog


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification (detail)"""
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_name', 'user_email',
            'title', 'message', 'notification_type',
            'notification_type_display', 'priority', 'priority_display',
            'is_read', 'read_at', 'link',
            'related_object_id', 'related_object_type',
            'sent_via_email', 'sent_via_sms',
            'email_sent_at', 'sms_sent_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationListSerializer(serializers.ModelSerializer):
    """Serializer for Notification (list view)"""
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type',
            'notification_type_display', 'priority', 'priority_display',
            'is_read', 'read_at', 'link', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for User Notification Preferences"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = UserNotificationPreference
        fields = [
            'id', 'user', 'user_name', 'user_email',
            'enable_email', 'enable_sms', 'enable_dashboard',
            'job_approved', 'job_rejected', 'application_received',
            'application_status', 'interview_scheduled', 'offer_extended',
            'payment_confirmed', 'payment_refunded', 'account_approved',
            'account_suspended', 'account_activated',
            'system_notifications', 'general_notifications',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationLogSerializer(serializers.ModelSerializer):
    """Serializer for Notification Log"""
    channel_display = serializers.CharField(source='get_channel_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    notification_title = serializers.CharField(source='notification.title', read_only=True)
    
    class Meta:
        model = NotificationLog
        fields = [
            'id', 'notification', 'notification_title',
            'channel', 'channel_display',
            'status', 'status_display',
            'error_message', 'sent_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']