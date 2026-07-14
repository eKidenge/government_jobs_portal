"""
Notifications Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.core.paginator import Paginator

from .models import Notification, UserNotificationPreference


@login_required
def notification_list(request):
    """List all notifications for the user"""
    notifications = Notification.objects.filter(user=request.user)
    
    # Filter by read status
    filter_type = request.GET.get('filter')
    if filter_type == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_type == 'read':
        notifications = notifications.filter(is_read=True)
    
    paginator = Paginator(notifications, 20)
    page = request.GET.get('page')
    notifications = paginator.get_page(page)
    
    context = {
        'notifications': notifications,
        'filter_type': filter_type,
        'unread_count': Notification.objects.filter(user=request.user, is_read=False).count(),
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
                'message': n.message[:100],
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
    notification = get_object_or_404(Notification, id=notif_id, user=request.user)
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, 'Notification marked as read.')
    return redirect('notification_list')


@login_required
@require_POST
def mark_as_unread(request, notif_id):
    """Mark a notification as unread"""
    notification = get_object_or_404(Notification, id=notif_id, user=request.user)
    notification.mark_as_unread()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, 'Notification marked as unread.')
    return redirect('notification_list')


@login_required
@require_POST
def delete_notification(request, notif_id):
    """Delete a notification"""
    notification = get_object_or_404(Notification, id=notif_id, user=request.user)
    notification.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, 'Notification deleted.')
    return redirect('notification_list')


@login_required
@require_POST
def mark_all_read(request):
    """Mark all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True, read_at=timezone.now())
    messages.success(request, 'All notifications marked as read.')
    return redirect('notification_list')


@login_required
@require_POST
def delete_all_notifications(request):
    """Delete all notifications"""
    Notification.objects.filter(user=request.user).delete()
    messages.success(request, 'All notifications deleted.')
    return redirect('notification_list')


@login_required
@require_GET
def unread_count(request):
    """Get unread notification count (AJAX)"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def notification_preferences(request):
    """View and update notification preferences"""
    try:
        preferences = UserNotificationPreference.objects.get(user=request.user)
    except UserNotificationPreference.DoesNotExist:
        preferences = UserNotificationPreference.objects.create(user=request.user)
    
    if request.method == 'POST':
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
    
    # Update preferences from POST data
    for field in ['enable_email', 'enable_sms', 'enable_dashboard',
                  'job_approved', 'job_rejected', 'application_received',
                  'application_status', 'interview_scheduled', 'offer_extended',
                  'payment_confirmed', 'payment_refunded', 'account_approved',
                  'account_suspended', 'account_activated', 'system_notifications',
                  'general_notifications']:
        if field in request.POST:
            setattr(preferences, field, request.POST[field] == 'true')
    
    preferences.save()
    
    return JsonResponse({'success': True, 'message': 'Preferences updated successfully!'})