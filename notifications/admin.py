"""
Notifications App Admin Configuration
"""
from django.contrib import admin
from .models import Notification, UserNotificationPreference, NotificationLog


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'priority', 'is_read', 'created_at')
    list_filter = ('notification_type', 'priority', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__email', 'user__full_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Notification', {
            'fields': ('user', 'title', 'message', 'notification_type', 'priority')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Delivery', {
            'fields': ('sent_via_email', 'sent_via_sms', 'email_sent_at', 'sms_sent_at')
        }),
        ('Links', {
            'fields': ('link', 'related_object_id', 'related_object_type')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread', 'send_email']
    
    def mark_as_read(self, request, queryset):
        count = 0
        for notification in queryset:
            notification.mark_as_read()
            count += 1
        self.message_user(request, f"{count} notifications marked as read.")
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        count = 0
        for notification in queryset:
            notification.mark_as_unread()
            count += 1
        self.message_user(request, f"{count} notifications marked as unread.")
    mark_as_unread.short_description = "Mark selected notifications as unread"
    
    def send_email(self, request, queryset):
        count = 0
        for notification in queryset:
            notification.send_email()
            count += 1
        self.message_user(request, f"Email sent for {count} notifications.")
    send_email.short_description = "Send email for selected notifications"


@admin.register(UserNotificationPreference)
class UserNotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'enable_email', 'enable_sms', 'enable_dashboard')
    search_fields = ('user__email', 'user__full_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Channel Preferences', {
            'fields': ('enable_email', 'enable_sms', 'enable_dashboard')
        }),
        ('Notification Types', {
            'fields': (
                'job_approved', 'job_rejected', 'application_received',
                'application_status', 'interview_scheduled', 'offer_extended',
                'payment_confirmed', 'payment_refunded', 'account_approved',
                'account_suspended', 'account_activated', 'system_notifications',
                'general_notifications'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('notification', 'channel', 'status', 'sent_at', 'created_at')
    list_filter = ('channel', 'status', 'created_at')
    search_fields = ('notification__title', 'notification__user__email')
    readonly_fields = ('id', 'notification', 'channel', 'status', 'error_message', 'sent_at', 'created_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False