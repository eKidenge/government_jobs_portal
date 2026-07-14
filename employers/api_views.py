"""
Employers API Views
Handles API endpoints for employer management
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.utils import timezone

from .models import EmployerProfile, EmployerDocument
from .serializers import (
    EmployerSerializer,
    EmployerDetailSerializer,
    EmployerCreateSerializer,
    EmployerUpdateSerializer,
    EmployerDocumentSerializer,
)
from accounts.models import User
from jobs.models import Job, JobApplication
from notifications.models import Notification


class EmployerListView(generics.ListAPIView):
    """API endpoint for listing employers"""
    serializer_class = EmployerSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = EmployerProfile.objects.filter(
            is_verified=True
        ).select_related('user', 'country')
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(company_name__icontains=search) |
                Q(description__icontains=search) |
                Q(industry__icontains=search)
            )
        
        # Filter by industry
        industry = self.request.query_params.get('industry')
        if industry:
            queryset = queryset.filter(industry=industry)
        
        # Filter by country
        country = self.request.query_params.get('country')
        if country:
            queryset = queryset.filter(country_id=country)
        
        # Annotate with job count
        queryset = queryset.annotate(
            job_count=Count('jobs', filter=Q(jobs__status='active', jobs__closing_date__gte=timezone.now()))
        )
        
        return queryset.order_by('company_name')


class EmployerDetailView(generics.RetrieveAPIView):
    """API endpoint for getting employer details"""
    serializer_class = EmployerDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'
    
    def get_queryset(self):
        return EmployerProfile.objects.filter(
            is_verified=True
        ).select_related('user', 'country')


class EmployerRegisterView(APIView):
    """API endpoint for employer registration"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = EmployerCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create user
        user_data = serializer.validated_data
        user = User.objects.create_user(
            email=user_data['email'],
            password=user_data['password'],
            full_name=user_data['full_name'],
            phone_number=user_data.get('phone_number', ''),
            user_type='employer',
            status='pending'
        )
        
        # Create employer profile
        employer = EmployerProfile.objects.create(
            user=user,
            company_name=user_data.get('company_name', ''),
            contact_email=user.email,
            contact_phone=user.phone_number,
            is_verified=False
        )
        
        return Response({
            'success': True,
            'message': 'Employer account created successfully. Please complete your profile.',
            'employer': EmployerSerializer(employer).data
        }, status=status.HTTP_201_CREATED)


class EmployerSetupView(APIView):
    """API endpoint for completing employer profile setup"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if request.user.user_type != 'employer':
            return Response({
                'success': False,
                'error': 'Access denied. This is for employers only.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            employer = EmployerProfile.objects.get(user=request.user)
        except EmployerProfile.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Employer profile not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EmployerUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Update employer profile
        for key, value in serializer.validated_data.items():
            setattr(employer, key, value)
        employer.save()
        
        return Response({
            'success': True,
            'message': 'Employer profile updated successfully',
            'employer': EmployerDetailSerializer(employer).data
        })


class EmployerVerificationView(APIView):
    """API endpoint for uploading verification documents"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if request.user.user_type != 'employer':
            return Response({
                'success': False,
                'error': 'Access denied. This is for employers only.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            employer = EmployerProfile.objects.get(user=request.user)
        except EmployerProfile.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Employer profile not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        document_type = request.data.get('document_type')
        document_file = request.FILES.get('document')
        
        if not document_type or not document_file:
            return Response({
                'success': False,
                'error': 'Please provide document type and file.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        doc = EmployerDocument.objects.create(
            employer=employer,
            document_type=document_type,
            document=document_file,
            description=request.data.get('description', '')
        )
        
        return Response({
            'success': True,
            'message': 'Document uploaded successfully',
            'document': EmployerDocumentSerializer(doc).data
        }, status=status.HTTP_201_CREATED)


class EmployerProfileUpdateView(APIView):
    """API endpoint for updating employer profile"""
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request):
        if request.user.user_type != 'employer':
            return Response({
                'success': False,
                'error': 'Access denied. This is for employers only.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            employer = EmployerProfile.objects.get(user=request.user)
        except EmployerProfile.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Employer profile not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EmployerUpdateSerializer(employer, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Update user info if provided
        if 'full_name' in request.data:
            request.user.full_name = request.data['full_name']
        if 'phone_number' in request.data:
            request.user.phone_number = request.data['phone_number']
        request.user.save()
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'employer': EmployerDetailSerializer(employer).data
        })


class EmployerLogoUploadView(APIView):
    """API endpoint for uploading employer logo"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if request.user.user_type != 'employer':
            return Response({
                'success': False,
                'error': 'Access denied. This is for employers only.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            employer = EmployerProfile.objects.get(user=request.user)
        except EmployerProfile.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Employer profile not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if 'logo' not in request.FILES:
            return Response({
                'success': False,
                'error': 'No logo file provided.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        employer.logo = request.FILES['logo']
        employer.save()
        
        return Response({
            'success': True,
            'message': 'Logo uploaded successfully',
            'logo_url': employer.logo.url if employer.logo else None
        })


class EmployerDocumentUploadView(APIView):
    """API endpoint for uploading employer documents"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if request.user.user_type != 'employer':
            return Response({
                'success': False,
                'error': 'Access denied. This is for employers only.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            employer = EmployerProfile.objects.get(user=request.user)
        except EmployerProfile.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Employer profile not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        document_type = request.data.get('document_type')
        document_file = request.FILES.get('document')
        
        if not document_type or not document_file:
            return Response({
                'success': False,
                'error': 'Please provide document type and file.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        doc = EmployerDocument.objects.create(
            employer=employer,
            document_type=document_type,
            document=document_file,
            description=request.data.get('description', '')
        )
        
        return Response({
            'success': True,
            'message': 'Document uploaded successfully',
            'document': EmployerDocumentSerializer(doc).data
        }, status=status.HTTP_201_CREATED)


class EmployerDocumentDeleteView(APIView):
    """API endpoint for deleting employer document"""
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, doc_id):
        if request.user.user_type != 'employer':
            return Response({
                'success': False,
                'error': 'Access denied. This is for employers only.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        doc = get_object_or_404(EmployerDocument, id=doc_id, employer__user=request.user)
        doc.delete()
        
        return Response({
            'success': True,
            'message': 'Document deleted successfully'
        })


class EmployerStatsView(APIView):
    """API endpoint for getting employer statistics"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.user_type != 'employer':
            return Response({
                'success': False,
                'error': 'Access denied. This is for employers only.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            employer = EmployerProfile.objects.get(user=request.user)
        except EmployerProfile.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Employer profile not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        jobs = Job.objects.filter(employer=employer)
        applications = JobApplication.objects.filter(job__employer=employer)
        
        stats = {
            'company_name': employer.company_name,
            'is_verified': employer.is_verified,
            'total_jobs': jobs.count(),
            'active_jobs': jobs.filter(status='active').count(),
            'pending_jobs': jobs.filter(status='pending').count(),
            'rejected_jobs': jobs.filter(status='rejected').count(),
            'total_applications': applications.count(),
            'applications_by_status': {
                'submitted': applications.filter(status='submitted').count(),
                'under_review': applications.filter(status='under_review').count(),
                'shortlisted': applications.filter(status='shortlisted').count(),
                'interview_scheduled': applications.filter(status='interview_scheduled').count(),
                'accepted': applications.filter(status='accepted').count(),
                'rejected': applications.filter(status='rejected').count(),
            },
            'total_views': jobs.aggregate(Sum('views_count'))['views_count__sum'] or 0,
        }
        return Response(stats)