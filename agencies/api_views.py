"""
Agencies API Views (Recruitment Agencies)
Handles API endpoints for recruitment agency management
"""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Sum
from django.utils import timezone

from .models import RecruitmentAgency, AgencyDocument, AgencyApplication, AgencyContract, AgencyRecruitmentProcess
from .serializers import (
    AgencySerializer,
    AgencyDetailSerializer,
    AgencyCreateSerializer,
    AgencyUpdateSerializer,
    AgencyDocumentSerializer,
    AgencyApplicationSerializer,
    AgencyContractSerializer,
    AgencyRecruitmentProcessSerializer,
    AgencyJobSerializer,  # Add this line
)
from accounts.models import User
from jobs.models import Job, JobApplication, Country
from notifications.models import Notification

class AgencyListView(generics.ListAPIView):
    """API endpoint for listing recruitment agencies"""
    serializer_class = AgencySerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = RecruitmentAgency.objects.filter(
            is_verified=True
        ).select_related('user', 'country')
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(agency_name__icontains=search) |
                Q(description__icontains=search) |
                Q(specializations__icontains=search)
            )
        
        # Filter by country
        country = self.request.query_params.get('country')
        if country:
            queryset = queryset.filter(country_id=country)
        
        # Annotate with job count
        queryset = queryset.annotate(
            job_count=Count('jobs', filter=Q(jobs__status='active', jobs__closing_date__gte=timezone.now()))
        )
        
        return queryset.order_by('agency_name')


class AgencyDetailView(generics.RetrieveAPIView):
    """API endpoint for getting agency details"""
    serializer_class = AgencyDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'
    
    def get_queryset(self):
        return RecruitmentAgency.objects.filter(
            is_verified=True
        ).select_related('user', 'country').prefetch_related('active_countries')


class AgencyRegisterView(APIView):
    """API endpoint for agency registration"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = AgencyCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create user
        user_data = serializer.validated_data
        user = User.objects.create_user(
            email=user_data['email'],
            password=user_data['password'],
            full_name=user_data['full_name'],
            phone_number=user_data.get('phone_number', ''),
            user_type='agency',
            status='pending'
        )
        
        # Create agency profile
        agency = RecruitmentAgency.objects.create(
            user=user,
            agency_name=user_data.get('agency_name', ''),
            contact_email=user.email,
            contact_phone=user.phone_number,
            is_verified=False
        )
        
        return Response({
            'success': True,
            'message': 'Agency account created successfully. Please complete your profile.',
            'agency': AgencySerializer(agency).data
        }, status=status.HTTP_201_CREATED)


class AgencySetupView(APIView):
    """API endpoint for completing agency profile setup"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if request.user.user_type != 'agency':
            return Response({
                'success': False,
                'error': 'Access denied. This is for recruitment agencies only.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            agency = RecruitmentAgency.objects.get(user=request.user)
        except RecruitmentAgency.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Agency profile not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AgencyUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Update agency profile
        for key, value in serializer.validated_data.items():
            setattr(agency, key, value)
        agency.save()
        
        # Save active countries if provided
        if 'active_countries' in request.data:
            country_ids = request.data.get('active_countries', [])
            if country_ids:
                agency.active_countries.set(country_ids)
        
        return Response({
            'success': True,
            'message': 'Agency profile updated successfully',
            'agency': AgencyDetailSerializer(agency).data
        })


class AgencyVerificationView(APIView):
    """API endpoint for uploading accreditation documents"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if request.user.user_type != 'agency':
            return Response({
                'success': False,
                'error': 'Access denied. This is for recruitment agencies only.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            agency = RecruitmentAgency.objects.get(user=request.user)
        except RecruitmentAgency.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Agency profile not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        document_type = request.data.get('document_type')
        document_file = request.FILES.get('document')
        
        if not document_type or not document_file:
            return Response({
                'success': False,
                'error': 'Please provide document type and file.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        doc = AgencyDocument.objects.create(
            agency=agency,
            document_type=document_type,
            document=document_file,
            description=request.data.get('description', '')
        )
        
        return Response({
            'success': True,
            'message': 'Document uploaded successfully',
            'document': AgencyDocumentSerializer(doc).data
        }, status=status.HTTP_201_CREATED)


class AgencyProfileUpdateView(APIView):
    """API endpoint for updating agency profile"""
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request):
        if request.user.user_type != 'agency':
            return Response({
                'success': False,
                'error': 'Access denied. This is for recruitment agencies only.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            agency = RecruitmentAgency.objects.get(user=request.user)
        except RecruitmentAgency.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Agency profile not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AgencyUpdateSerializer(agency, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Save active countries if provided
        if 'active_countries' in request.data:
            country_ids = request.data.get('active_countries', [])
            if country_ids:
                agency.active_countries.set(country_ids)
        
        # Update user info if provided
        if 'full_name' in request.data:
            request.user.full_name = request.data['full_name']
        if 'phone_number' in request.data:
            request.user.phone_number = request.data['phone_number']
        request.user.save()
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'agency': AgencyDetailSerializer(agency).data
        })


class AgencyLogoUploadView(APIView):
    """API endpoint for uploading agency logo"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if request.user.user_type != 'agency':
            return Response({
                'success': False,
                'error': 'Access denied. This is for recruitment agencies only.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            agency = RecruitmentAgency.objects.get(user=request.user)
        except RecruitmentAgency.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Agency profile not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if 'logo' not in request.FILES:
            return Response({
                'success': False,
                'error': 'No logo file provided.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        agency.logo = request.FILES['logo']
        agency.save()
        
        return Response({
            'success': True,
            'message': 'Logo uploaded successfully',
            'logo_url': agency.logo.url if agency.logo else None
        })


class AgencyDocumentUploadView(APIView):
    """API endpoint for uploading agency documents"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if request.user.user_type != 'agency':
            return Response({
                'success': False,
                'error': 'Access denied. This is for recruitment agencies only.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            agency = RecruitmentAgency.objects.get(user=request.user)
        except RecruitmentAgency.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Agency profile not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        document_type = request.data.get('document_type')
        document_file = request.FILES.get('document')
        
        if not document_type or not document_file:
            return Response({
                'success': False,
                'error': 'Please provide document type and file.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        doc = AgencyDocument.objects.create(
            agency=agency,
            document_type=document_type,
            document=document_file,
            description=request.data.get('description', '')
        )
        
        return Response({
            'success': True,
            'message': 'Document uploaded successfully',
            'document': AgencyDocumentSerializer(doc).data
        }, status=status.HTTP_201_CREATED)


class AgencyDocumentDeleteView(APIView):
    """API endpoint for deleting agency document"""
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, doc_id):
        if request.user.user_type != 'agency':
            return Response({
                'success': False,
                'error': 'Access denied. This is for recruitment agencies only.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        doc = get_object_or_404(AgencyDocument, id=doc_id, agency__user=request.user)
        doc.delete()
        
        return Response({
            'success': True,
            'message': 'Document deleted successfully'
        })


class AgencyJobsView(generics.ListAPIView):
    """API endpoint for getting agency jobs"""
    serializer_class = AgencyJobSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.user_type != 'agency':
            return Job.objects.none()
        
        try:
            agency = RecruitmentAgency.objects.get(user=self.request.user)
            return Job.objects.filter(agency=agency).order_by('-posted_date')
        except RecruitmentAgency.DoesNotExist:
            return Job.objects.none()


class AgencyJobCreateView(APIView):
    """API endpoint for agency to create a job"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        if request.user.user_type != 'agency':
            return Response({
                'success': False,
                'error': 'Access denied. This is for recruitment agencies only.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            agency = RecruitmentAgency.objects.get(user=request.user)
            if not agency.is_verified:
                return Response({
                    'success': False,
                    'error': 'Your agency must be verified before posting jobs.'
                }, status=status.HTTP_403_FORBIDDEN)
        except RecruitmentAgency.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Agency profile not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        from jobs.serializers import JobDetailSerializer
        serializer = JobDetailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        job = serializer.save(
            agency=agency,
            status='pending',
            posted_by=request.user
        )
        
        return Response({
            'success': True,
            'message': 'Job posted successfully. It will be reviewed by the admin.',
            'job': JobDetailSerializer(job).data
        }, status=status.HTTP_201_CREATED)


class AgencyJobUpdateView(APIView):
    """API endpoint for agency to update a job"""
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, pk):
        if request.user.user_type != 'agency':
            return Response({
                'success': False,
                'error': 'Access denied. This is for recruitment agencies only.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            agency = RecruitmentAgency.objects.get(user=request.user)
        except RecruitmentAgency.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Agency profile not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        job = get_object_or_404(Job, id=pk, agency=agency)
        
        if job.status in ['approved', 'active']:
            return Response({
                'success': False,
                'error': 'This job is already live. Only pending jobs can be edited.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from jobs.serializers import JobDetailSerializer
        serializer = JobDetailSerializer(job, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'success': True,
            'message': 'Job updated successfully',
            'job': serializer.data
        })


class AgencyStatsView(APIView):
    """API endpoint for getting agency statistics"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.user_type != 'agency':
            return Response({
                'success': False,
                'error': 'Access denied. This is for recruitment agencies only.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            agency = RecruitmentAgency.objects.get(user=request.user)
        except RecruitmentAgency.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Agency profile not found.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        jobs = Job.objects.filter(agency=agency)
        applications = JobApplication.objects.filter(job__agency=agency)
        agency_applications = AgencyApplication.objects.filter(agency=agency)
        
        stats = {
            'agency_name': agency.agency_name,
            'is_verified': agency.is_verified,
            'license_valid': agency.is_license_valid(),
            'license_expiry': agency.license_expiry.strftime('%Y-%m-%d') if agency.license_expiry else None,
            'total_jobs': jobs.count(),
            'active_jobs': jobs.filter(status='active').count(),
            'pending_jobs': jobs.filter(status='pending').count(),
            'total_applications': applications.count(),
            'agency_applications': agency_applications.count(),
            'applications_by_status': {
                'pending': agency_applications.filter(status='pending').count(),
                'processing': agency_applications.filter(status='processing').count(),
                'submitted': agency_applications.filter(status='submitted').count(),
                'interview': agency_applications.filter(status='interview').count(),
                'offer': agency_applications.filter(status='offer').count(),
                'accepted': agency_applications.filter(status='accepted').count(),
                'rejected': agency_applications.filter(status='rejected').count(),
            },
            'active_countries': agency.active_countries.count(),
            'total_views': jobs.aggregate(Sum('views_count'))['views_count__sum'] or 0,
        }
        return Response(stats)