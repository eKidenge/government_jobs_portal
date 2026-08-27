"""
Notifications App URLs
"""
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notification List
    path('', views.notification_list, name='notification_list'),
    path('unread/', views.unread_notifications, name='unread_notifications'),
    
    # Individual Notification Actions
    path('<uuid:notif_id>/read/', views.mark_as_read, name='mark_as_read'),
    path('<uuid:notif_id>/unread/', views.mark_as_unread, name='mark_as_unread'),
    path('<uuid:notif_id>/delete/', views.delete_notification, name='delete_notification'),
    
    # Bulk Actions
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('delete-all/', views.delete_all_notifications, name='delete_all_notifications'),
    
    # Notification Count (AJAX)
    path('unread-count/', views.unread_count, name='unread_count'),
    
    # Notification Preferences
    path('preferences/', views.notification_preferences, name='notification_preferences'),
    path('preferences/update/', views.update_notification_preferences, name='update_notification_preferences'),
]
