"""
Notifications App URLs
"""
from django.urls import path
from . import views

urlpatterns = [
    # Notification List
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/unread/', views.unread_notifications, name='unread_notifications'),
    
    # Notification Actions
    path('notifications/<uuid:notif_id>/read/', views.mark_as_read, name='mark_as_read'),
    path('notifications/<uuid:notif_id>/unread/', views.mark_as_unread, name='mark_as_unread'),
    path('notifications/<uuid:notif_id>/delete/', views.delete_notification, name='delete_notification'),
    
    # Bulk Actions
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('notifications/delete-all/', views.delete_all_notifications, name='delete_all_notifications'),
    
    # Notification Count (AJAX)
    path('notifications/unread-count/', views.unread_count, name='unread_count'),
    
    # Notification Preferences
    path('notifications/preferences/', views.notification_preferences, name='notification_preferences'),
    path('notifications/preferences/update/', views.update_notification_preferences, name='update_notification_preferences'),
]