"""
Notifications API Views
Handles API endpoints for notifications
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Notification, UserNotificationPreference
from .serializers import (
    NotificationSerializer,
    NotificationListSerializer,
    NotificationPreferenceSerializer,
)


class NotificationListView(generics.ListAPIView):
    """API endpoint for listing user notifications"""
    serializer_class = NotificationListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Notification.objects.filter(user=self.request.user)
        
        # Filter by read status
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            if is_read.lower() == 'true':
                queryset = queryset.filter(is_read=True)
            elif is_read.lower() == 'false':
                queryset = queryset.filter(is_read=False)
        
        # Filter by notification type
        notification_type = self.request.query_params.get('notification_type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset.order_by('-created_at')


class NotificationDetailView(generics.RetrieveAPIView):
    """API endpoint for getting notification details"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Auto-mark as read when viewed in detail
        if not instance.is_read:
            instance.mark_as_read()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class MarkNotificationReadView(APIView):
    """API endpoint for marking a notification as read"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        notification = get_object_or_404(Notification, id=pk, user=request.user)
        notification.mark_as_read()
        
        return Response({
            'success': True,
            'message': 'Notification marked as read',
            'notification': NotificationSerializer(notification).data
        })


class MarkNotificationUnreadView(APIView):
    """API endpoint for marking a notification as unread"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        notification = get_object_or_404(Notification, id=pk, user=request.user)
        notification.mark_as_unread()
        
        return Response({
            'success': True,
            'message': 'Notification marked as unread',
            'notification': NotificationSerializer(notification).data
        })


class DeleteNotificationView(APIView):
    """API endpoint for deleting a notification"""
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, pk):
        notification = get_object_or_404(Notification, id=pk, user=request.user)
        notification.delete()
        
        return Response({
            'success': True,
            'message': 'Notification deleted successfully'
        })


class MarkAllNotificationsReadView(APIView):
    """API endpoint for marking all notifications as read"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        
        return Response({
            'success': True,
            'message': f'{count} notifications marked as read',
            'count': count
        })


class DeleteAllNotificationsView(APIView):
    """API endpoint for deleting all notifications"""
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request):
        count = Notification.objects.filter(user=request.user).count()
        Notification.objects.filter(user=request.user).delete()
        
        return Response({
            'success': True,
            'message': f'{count} notifications deleted',
            'count': count
        })


class UnreadNotificationCountView(APIView):
    """API endpoint for getting unread notification count"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return Response({
            'success': True,
            'count': count
        })


class NotificationPreferencesView(generics.RetrieveAPIView):
    """API endpoint for getting user notification preferences"""
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        try:
            return UserNotificationPreference.objects.get(user=self.request.user)
        except UserNotificationPreference.DoesNotExist:
            # Create default preferences
            return UserNotificationPreference.objects.create(user=self.request.user)


class UpdateNotificationPreferencesView(APIView):
    """API endpoint for updating user notification preferences"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            preferences = UserNotificationPreference.objects.get(user=request.user)
        except UserNotificationPreference.DoesNotExist:
            preferences = UserNotificationPreference.objects.create(user=request.user)
        
        serializer = NotificationPreferenceSerializer(preferences, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'success': True,
            'message': 'Notification preferences updated successfully',
            'preferences': serializer.data
        })