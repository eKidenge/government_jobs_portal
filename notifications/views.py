"""
Notifications Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.core.paginator import Paginator
from django.utils import timezone
import logging

from .models import Notification, UserNotificationPreference

logger = logging.getLogger(__name__)


@login_required
def notification_list(request):
    """List all notifications for the user"""
    notifications = Notification.objects.filter(user=request.user)
    
    # Filter by read status
    filter_type = request.GET.get('filter', 'all')
    if filter_type == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_type == 'read':
        notifications = notifications.filter(is_read=True)
    
    # Order by most recent first
    notifications = notifications.order_by('-created_at')
    
    paginator = Paginator(notifications, 20)
    page = request.GET.get('page')
    notifications = paginator.get_page(page)
    
    context = {
        'notifications': notifications,
        'filter_type': filter_type,
        'unread_count': Notification.objects.filter(user=request.user, is_read=False).count(),
        'now': timezone.now(),
    }
    return render(request, 'notifications/list.html', context)


@login_required
def unread_notifications(request):
    """Get unread notifications (AJAX)"""
    notifications = Notification.objects.filter(
        user=request.user, 
        is_read=False
    ).order_by('-created_at')[:10]
    
    data = {
        'count': notifications.count(),
        'notifications': [
            {
                'id': str(n.id),
                'title': n.title,
                'message': n.message[:100] + ('...' if len(n.message) > 100 else ''),
                'created_at': n.created_at.strftime('%Y-%m-%d %H:%M'),
                'link': n.link,
                'priority': n.priority,
            }
            for n in notifications
        ]
    }
    return JsonResponse(data)


@login_required
@require_POST
def mark_as_read(request, notif_id):
    """Mark a notification as read"""
    try:
        notification = get_object_or_404(Notification, id=notif_id, user=request.user)
        notification.mark_as_read()
        
        # Get updated unread count
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Notification marked as read',
                'unread_count': unread_count
            })
        
        messages.success(request, 'Notification marked as read.')
        return redirect('notification_list')
    
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Failed to mark notification as read'
            }, status=500)
        messages.error(request, 'Failed to mark notification as read.')
        return redirect('notification_list')


@login_required
@require_POST
def mark_as_unread(request, notif_id):
    """Mark a notification as unread"""
    try:
        notification = get_object_or_404(Notification, id=notif_id, user=request.user)
        notification.mark_as_unread()
        
        # Get updated unread count
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Notification marked as unread',
                'unread_count': unread_count
            })
        
        messages.success(request, 'Notification marked as unread.')
        return redirect('notification_list')
    
    except Exception as e:
        logger.error(f"Error marking notification as unread: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Failed to mark notification as unread'
            }, status=500)
        messages.error(request, 'Failed to mark notification as unread.')
        return redirect('notification_list')


@login_required
@require_POST
def delete_notification(request, notif_id):
    """Delete a notification"""
    try:
        notification = get_object_or_404(Notification, id=notif_id, user=request.user)
        notification.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Notification deleted'
            })
        
        messages.success(request, 'Notification deleted.')
        return redirect('notification_list')
    
    except Exception as e:
        logger.error(f"Error deleting notification: {e}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Failed to delete notification'
            }, status=500)
        messages.error(request, 'Failed to delete notification.')
        return redirect('notification_list')


@login_required
@require_POST
def mark_all_read(request):
    """Mark all notifications as read"""
    try:
        updated_count = Notification.objects.filter(
            user=request.user, 
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        messages.success(request, f'All {updated_count} notification{"s" if updated_count != 1 else ""} marked as read.')
        return redirect('notification_list')
    
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {e}")
        messages.error(request, 'Failed to mark all notifications as read.')
        return redirect('notification_list')


@login_required
@require_POST
def delete_all_notifications(request):
    """Delete all notifications"""
    try:
        count = Notification.objects.filter(user=request.user).count()
        Notification.objects.filter(user=request.user).delete()
        
        messages.success(request, f'All {count} notification{"s" if count != 1 else ""} deleted.')
        return redirect('notification_list')
    
    except Exception as e:
        logger.error(f"Error deleting all notifications: {e}")
        messages.error(request, 'Failed to delete all notifications.')
        return redirect('notification_list')


@login_required
@require_GET
def unread_count(request):
    """
    Get unread notification count (AJAX)
    Returns JSON with unread count for authenticated users
    """
    try:
        if not request.user.is_authenticated:
            return JsonResponse({
                'error': 'Authentication required',
                'count': 0,
                'success': False
            }, status=401)
        
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        
        return JsonResponse({
            'count': count,
            'success': True,
        })
    
    except Exception as e:
        logger.error(f"Error fetching unread count: {e}")
        return JsonResponse({
            'count': 0,
            'error': str(e),
            'success': False
        }, status=500)


@login_required
def notification_preferences(request):
    """View and update notification preferences"""
    try:
        preferences = UserNotificationPreference.objects.get(user=request.user)
    except UserNotificationPreference.DoesNotExist:
        preferences = UserNotificationPreference.objects.create(user=request.user)
    
    if request.method == 'POST':
        try:
            # Update preferences
            preferences.enable_email = request.POST.get('enable_email') == 'on'
            preferences.enable_sms = request.POST.get('enable_sms') == 'on'
            preferences.enable_dashboard = request.POST.get('enable_dashboard') == 'on'
            
            preferences.job_approved = request.POST.get('job_approved') == 'on'
            preferences.job_rejected = request.POST.get('job_rejected') == 'on'
            preferences.application_received = request.POST.get('application_received') == 'on'
            preferences.application_status = request.POST.get('application_status') == 'on'
            preferences.interview_scheduled = request.POST.get('interview_scheduled') == 'on'
            preferences.offer_extended = request.POST.get('offer_extended') == 'on'
            preferences.payment_confirmed = request.POST.get('payment_confirmed') == 'on'
            preferences.payment_refunded = request.POST.get('payment_refunded') == 'on'
            preferences.account_approved = request.POST.get('account_approved') == 'on'
            preferences.account_suspended = request.POST.get('account_suspended') == 'on'
            preferences.account_activated = request.POST.get('account_activated') == 'on'
            preferences.system_notifications = request.POST.get('system_notifications') == 'on'
            preferences.general_notifications = request.POST.get('general_notifications') == 'on'
            
            preferences.save()
            messages.success(request, 'Notification preferences updated successfully!')
            return redirect('notification_preferences')
        
        except Exception as e:
            logger.error(f"Error updating preferences: {e}")
            messages.error(request, 'Failed to update preferences. Please try again.')
    
    context = {
        'preferences': preferences,
    }
    return render(request, 'notifications/preferences.html', context)


@login_required
@require_POST
def update_notification_preferences(request):
    """Update notification preferences (AJAX)"""
    try:
        preferences = UserNotificationPreference.objects.get(user=request.user)
    except UserNotificationPreference.DoesNotExist:
        preferences = UserNotificationPreference.objects.create(user=request.user)
    
    try:
        # Update preferences from POST data
        for field in ['enable_email', 'enable_sms', 'enable_dashboard',
                      'job_approved', 'job_rejected', 'application_received',
                      'application_status', 'interview_scheduled', 'offer_extended',
                      'payment_confirmed', 'payment_refunded', 'account_approved',
                      'account_suspended', 'account_activated', 'system_notifications',
                      'general_notifications']:
            if field in request.POST:
                value = request.POST.get(field)
                if value.lower() in ['true', 'on', '1']:
                    setattr(preferences, field, True)
                elif value.lower() in ['false', 'off', '0']:
                    setattr(preferences, field, False)
        
        preferences.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Preferences updated successfully!'
        })
    
    except Exception as e:
        logger.error(f"Error updating preferences via AJAX: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to update preferences'
        }, status=500)
