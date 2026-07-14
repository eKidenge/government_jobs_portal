"""
Notifications App API URLs
"""
from django.urls import path
from .api_views import (
    NotificationListView,
    NotificationDetailView,
    MarkNotificationReadView,
    MarkNotificationUnreadView,
    DeleteNotificationView,
    MarkAllNotificationsReadView,
    DeleteAllNotificationsView,
    UnreadNotificationCountView,
    NotificationPreferencesView,
    UpdateNotificationPreferencesView,
)

app_name = 'notifications_api'

urlpatterns = [
    # Notification List
    path('', NotificationListView.as_view(), name='api_notification_list'),
    path('unread/', UnreadNotificationCountView.as_view(), name='api_unread_notifications'),
    
    # Individual Notification Actions
    path('<uuid:pk>/', NotificationDetailView.as_view(), name='api_notification_detail'),
    path('<uuid:pk>/read/', MarkNotificationReadView.as_view(), name='api_mark_read'),
    path('<uuid:pk>/unread/', MarkNotificationUnreadView.as_view(), name='api_mark_unread'),
    path('<uuid:pk>/delete/', DeleteNotificationView.as_view(), name='api_delete_notification'),
    
    # Bulk Actions
    path('mark-all-read/', MarkAllNotificationsReadView.as_view(), name='api_mark_all_read'),
    path('delete-all/', DeleteAllNotificationsView.as_view(), name='api_delete_all'),
    
    # Preferences
    path('preferences/', NotificationPreferencesView.as_view(), name='api_notification_preferences'),
    path('preferences/update/', UpdateNotificationPreferencesView.as_view(), name='api_update_preferences'),
]