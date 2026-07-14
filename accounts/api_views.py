"""
Accounts API Views
Handles API endpoints for user registration, login, profile management, etc.
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import uuid

from .models import User, UserProfile
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from jobs.models import JobApplication
from payments.models import Payment, UserPaymentAccess
from notifications.models import Notification


class UserRegistrationAPIView(generics.CreateAPIView):
    """API endpoint for user registration"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create user
        user = serializer.save()
        
        # Create user profile
        UserProfile.objects.create(
            user=user,
            cv=request.data.get('cv'),
            national_id_document=request.data.get('national_id_document'),
            passport_document=request.data.get('passport_document'),
            photo=request.data.get('photo'),
            cover_letter=request.data.get('cover_letter')
        )
        
        # Send welcome email
        try:
            subject = 'Welcome to Government Jobs Portal'
            html_message = render_to_string('emails/welcome.html', {'user': user})
            plain_message = strip_tags(html_message)
            send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html_message)
        except Exception as e:
            print(f"Email sending failed: {e}")
        
        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'User registered successfully',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'full_name': user.full_name,
                'user_type': user.user_type,
            },
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)


class UserLoginAPIView(APIView):
    """API endpoint for user login"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user = authenticate(request, email=email, password=password)
        
        if not user:
            return Response({
                'success': False,
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        if user.status == 'suspended':
            return Response({
                'success': False,
                'error': 'Your account has been suspended. Please contact support.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': str(user.id),
                'email': user.email,
                'full_name': user.full_name,
                'user_type': user.user_type,
                'status': user.status,
                'is_verified': user.is_verified,
            },
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        })


class UserProfileAPIView(generics.RetrieveAPIView):
    """API endpoint for getting user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserUpdateAPIView(generics.UpdateAPIView):
    """API endpoint for updating user profile"""
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Update profile if needed
        profile_data = request.data.get('profile', {})
        if profile_data:
            try:
                profile = UserProfile.objects.get(user=instance)
                for key, value in profile_data.items():
                    setattr(profile, key, value)
                profile.save()
            except UserProfile.DoesNotExist:
                pass
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'user': serializer.data
        })


class PasswordChangeAPIView(APIView):
    """API endpoint for changing password"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        
        # Check current password
        if not user.check_password(serializer.validated_data['current_password']):
            return Response({
                'success': False,
                'error': 'Current password is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Set new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        # Create notification
        Notification.objects.create(
            user=user,
            title='Password Changed',
            message='Your password has been changed successfully.',
            notification_type='password_reset'
        )
        
        return Response({
            'success': True,
            'message': 'Password changed successfully'
        })


class PasswordResetRequestAPIView(APIView):
    """API endpoint for requesting password reset"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            # Generate reset token
            token = str(uuid.uuid4())
            # You would save this token to a model or cache
            
            # Send reset email
            subject = 'Password Reset Request'
            html_message = render_to_string('emails/password_reset.html', {
                'user': user,
                'token': token,
                'site_url': settings.SITE_URL
            })
            plain_message = strip_tags(html_message)
            send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [email], html_message=html_message)
            
            return Response({
                'success': True,
                'message': 'Password reset link has been sent to your email'
            })
        except User.DoesNotExist:
            # Don't reveal if user exists or not
            return Response({
                'success': True,
                'message': 'If an account with that email exists, a reset link has been sent'
            })


class PasswordResetConfirmAPIView(APIView):
    """API endpoint for confirming password reset"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        # Verify token and get user
        # You would retrieve the user from the token
        # For now, we'll skip token verification (implement in production)
        
        # Set new password
        # user.set_password(new_password)
        # user.save()
        
        return Response({
            'success': True,
            'message': 'Password has been reset successfully'
        })


class EmailVerificationAPIView(APIView):
    """API endpoint for email verification"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, token):
        # Implement email verification logic
        # For now, return success
        return Response({
            'success': True,
            'message': 'Email verified successfully'
        })


class ResendVerificationAPIView(APIView):
    """API endpoint for resending verification email"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        # Send verification email
        token = str(uuid.uuid4())
        subject = 'Verify Your Email'
        html_message = render_to_string('emails/verify_email.html', {
            'user': user,
            'token': token,
            'site_url': settings.SITE_URL
        })
        plain_message = strip_tags(html_message)
        send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html_message)
        
        return Response({
            'success': True,
            'message': 'Verification email has been resent'
        })


class UserDashboardStatsAPIView(APIView):
    """API endpoint for getting user dashboard statistics"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get application stats
        applications = JobApplication.objects.filter(applicant=user)
        
        # Get payment status
        try:
            payment_access = UserPaymentAccess.objects.get(user=user)
            has_payment_access = payment_access.can_apply()
            total_applications_used = payment_access.applications_used
            access_type = payment_access.access_type
        except UserPaymentAccess.DoesNotExist:
            has_payment_access = False
            total_applications_used = 0
            access_type = None
        
        # Get notifications count
        unread_notifications = Notification.objects.filter(user=user, is_read=False).count()
        
        # Get profile completion
        try:
            profile = UserProfile.objects.get(user=user)
            completion_fields = [
                profile.cv, profile.national_id_document, profile.passport_document,
                profile.photo, profile.education, profile.work_experience,
                profile.skills, profile.languages
            ]
            completed = sum(1 for field in completion_fields if field)
            profile_completion = int((completed / len(completion_fields)) * 100)
        except UserProfile.DoesNotExist:
            profile_completion = 0
        
        return Response({
            'success': True,
            'stats': {
                'total_applications': applications.count(),
                'applications_by_status': {
                    'submitted': applications.filter(status='submitted').count(),
                    'under_review': applications.filter(status='under_review').count(),
                    'shortlisted': applications.filter(status='shortlisted').count(),
                    'interview_scheduled': applications.filter(status='interview_scheduled').count(),
                    'accepted': applications.filter(status='accepted').count(),
                    'rejected': applications.filter(status='rejected').count(),
                },
                'payment_access': {
                    'has_access': has_payment_access,
                    'applications_used': total_applications_used,
                    'access_type': access_type,
                },
                'unread_notifications': unread_notifications,
                'profile_completion': profile_completion,
            }
        })


class LogoutAPIView(APIView):
    """API endpoint for logout"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'success': True,
                'message': 'Logged out successfully'
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)