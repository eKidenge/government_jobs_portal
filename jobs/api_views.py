"""
Jobs API Views
Handles API endpoints for job listings, applications, and management
"""
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Job, Category, Country, JobApplication
from .serializers import (
    JobListSerializer,
    JobDetailSerializer,
    JobApplicationSerializer,
    JobApplicationCreateSerializer,
    JobApplicationStatusUpdateSerializer,
    CountrySerializer,
    CategorySerializer,
)
from accounts.models import User
from employers.models import EmployerProfile
from agencies.models import RecruitmentAgency
from payments.models import UserPaymentAccess
from notifications.models import Notification


class JobPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class JobListView(generics.ListAPIView):
    """API endpoint for listing jobs with filtering"""
    serializer_class = JobListSerializer
    pagination_class = JobPagination
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'requirements', 'employer__company_name', 'agency__agency_name']
    ordering_fields = ['posted_date', 'salary_min', 'salary_max', 'title']
    ordering = ['-posted_date']
    
    def get_queryset(self):
        queryset = Job.objects.filter(
            status='active',
            is_verified=True,
            closing_date__gte=timezone.now()
        ).select_related('country', 'category', 'employer', 'agency')
        
        # Filter by country
        country = self.request.query_params.get('country')
        if country:
            queryset = queryset.filter(country_id=country)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filter by employment type
        employment_type = self.request.query_params.get('employment_type')
        if employment_type:
            queryset = queryset.filter(employment_type=employment_type)
        
        # Filter by experience level
        experience_level = self.request.query_params.get('experience_level')
        if experience_level:
            queryset = queryset.filter(experience_level=experience_level)
        
        # Filter by salary range
        salary_min = self.request.query_params.get('salary_min')
        if salary_min:
            queryset = queryset.filter(salary_min__gte=salary_min)
        
        salary_max = self.request.query_params.get('salary_max')
        if salary_max:
            queryset = queryset.filter(salary_max__lte=salary_max)
        
        # Filter by featured
        featured = self.request.query_params.get('featured')
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset


class JobDetailView(generics.RetrieveAPIView):
    """API endpoint for getting job details"""
    serializer_class = JobDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'
    
    def get_queryset(self):
        return Job.objects.filter(
            status='active',
            is_verified=True,
            closing_date__gte=timezone.now()
        ).select_related('country', 'category', 'employer', 'agency')
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.views_count += 1
        instance.save(update_fields=['views_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class JobApplicationCreateView(APIView):
    """API endpoint for applying to a job"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, job_id):
        user = request.user
        
        # Check if user is a citizen
        if user.user_type != 'citizen':
            return Response({
                'success': False,
                'error': 'Only citizens can apply for jobs.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get job
        job = get_object_or_404(
            Job,
            id=job_id,
            status='active',
            is_verified=True,
            closing_date__gte=timezone.now()
        )
        
        # Check if user has payment access
        try:
            payment_access = UserPaymentAccess.objects.get(user=user)
            if not payment_access.can_apply():
                return Response({
                    'success': False,
                    'error': 'Please complete the government employment service fee payment before applying.'
                }, status=status.HTTP_403_FORBIDDEN)
        except UserPaymentAccess.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Please complete the government employment service fee payment before applying.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if already applied
        if JobApplication.objects.filter(job=job, applicant=user).exists():
            return Response({
                'success': False,
                'error': 'You have already applied for this position.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create application
        serializer = JobApplicationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        application = serializer.save(
            job=job,
            applicant=user,
            status='submitted'
        )
        
        # Update job application count
        job.applications_count += 1
        job.save(update_fields=['applications_count'])
        
        # Update payment access usage
        payment_access.applications_used += 1
        payment_access.save(update_fields=['applications_used'])
        
        # Create notification for applicant
        Notification.objects.create(
            user=user,
            title='Application Submitted',
            message=f'Your application for "{job.title}" has been submitted successfully.',
            notification_type='application_received',
            link=f'/jobs/{job.id}/'
        )
        
        # Notify employer/agency
        if job.employer:
            Notification.objects.create(
                user=job.employer.user,
                title='New Application Received',
                message=f'{user.full_name} has applied for "{job.title}".',
                notification_type='application_received',
                link=f'/employer/applications/{application.id}/'
            )
        elif job.agency:
            Notification.objects.create(
                user=job.agency.user,
                title='New Application Received',
                message=f'{user.full_name} has applied for "{job.title}".',
                notification_type='application_received',
                link=f'/agency/applications/{application.id}/'
            )
        
        return Response({
            'success': True,
            'message': 'Application submitted successfully',
            'application': JobApplicationSerializer(application).data
        }, status=status.HTTP_201_CREATED)


class MyApplicationsView(generics.ListAPIView):
    """API endpoint for getting user's applications"""
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = JobPagination
    
    def get_queryset(self):
        queryset = JobApplication.objects.filter(
            applicant=self.request.user
        ).select_related('job', 'job__employer', 'job__country', 'job__category')
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-date_applied')


class ApplicationDetailView(generics.RetrieveAPIView):
    """API endpoint for getting application details"""
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        return JobApplication.objects.filter(
            applicant=self.request.user
        ).select_related('job', 'job__employer', 'job__country', 'job__category')


class FeaturedJobsView(generics.ListAPIView):
    """API endpoint for getting featured jobs"""
    serializer_class = JobListSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Job.objects.filter(
            status='active',
            is_featured=True,
            is_verified=True,
            closing_date__gte=timezone.now()
        ).select_related('country', 'category', 'employer', 'agency').order_by('-posted_date')[:10]


class JobStatisticsView(APIView):
    """API endpoint for getting job statistics"""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        stats = {
            'available_jobs': Job.objects.filter(status='active', closing_date__gte=timezone.now()).count(),
            'registered_job_seekers': User.objects.filter(user_type='citizen', status='approved').count(),
            'verified_employers': EmployerProfile.objects.filter(is_verified=True).count(),
            'countries_recruiting': Job.objects.filter(status='active').values('country').distinct().count(),
            'successful_placements': JobApplication.objects.filter(status='accepted').count(),
            'licensed_recruitment_agencies': RecruitmentAgency.objects.filter(is_verified=True).count(),
        }
        return Response(stats)


class JobCategoriesView(generics.ListAPIView):
    """API endpoint for getting job categories"""
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Category.objects.filter(
            is_active=True,
            jobs__status='active',
            jobs__is_verified=True,
            jobs__closing_date__gte=timezone.now()
        ).annotate(
            job_count=Count('jobs')
        ).filter(job_count__gt=0).order_by('name')


class JobCountriesView(generics.ListAPIView):
    """API endpoint for getting countries with jobs"""
    serializer_class = CountrySerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Country.objects.filter(
            is_active=True,
            jobs__status='active',
            jobs__is_verified=True,
            jobs__closing_date__gte=timezone.now()
        ).annotate(
            job_count=Count('jobs')
        ).filter(job_count__gt=0).order_by('name')


class CountryJobsView(generics.ListAPIView):
    """API endpoint for getting jobs in a specific country"""
    serializer_class = JobListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = JobPagination
    
    def get_queryset(self):
        country = get_object_or_404(Country, slug=self.kwargs.get('country_slug'), is_active=True)
        return Job.objects.filter(
            country=country,
            status='active',
            is_verified=True,
            closing_date__gte=timezone.now()
        ).select_related('country', 'category', 'employer', 'agency').order_by('-posted_date')


class CategoryJobsView(generics.ListAPIView):
    """API endpoint for getting jobs in a specific category"""
    serializer_class = JobListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = JobPagination
    
    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs.get('category_slug'), is_active=True)
        return Job.objects.filter(
            category=category,
            status='active',
            is_verified=True,
            closing_date__gte=timezone.now()
        ).select_related('country', 'category', 'employer', 'agency').order_by('-posted_date')


# ==============================================
# EMPLOYER JOB MANAGEMENT API VIEWS
# ==============================================

class EmployerJobListView(generics.ListAPIView):
    """API endpoint for employer to list their jobs"""
    serializer_class = JobListSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = JobPagination
    
    def get_queryset(self):
        if self.request.user.user_type != 'employer':
            return Job.objects.none()
        
        try:
            employer = EmployerProfile.objects.get(user=self.request.user)
            return Job.objects.filter(employer=employer).order_by('-posted_date')
        except EmployerProfile.DoesNotExist:
            return Job.objects.none()


class EmployerJobCreateView(generics.CreateAPIView):
    """API endpoint for employer to create a job"""
    serializer_class = JobDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        if self.request.user.user_type != 'employer':
            raise PermissionError('Only employers can create jobs.')
        
        try:
            employer = EmployerProfile.objects.get(user=self.request.user)
            if not employer.is_verified:
                raise PermissionError('Your employer account must be verified before posting jobs.')
            
            serializer.save(
                employer=employer,
                status='pending',
                posted_by=self.request.user
            )
        except EmployerProfile.DoesNotExist:
            raise PermissionError('Please complete your employer profile first.')


class EmployerJobUpdateView(generics.UpdateAPIView):
    """API endpoint for employer to update a job"""
    serializer_class = JobDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        if self.request.user.user_type != 'employer':
            return Job.objects.none()
        
        try:
            employer = EmployerProfile.objects.get(user=self.request.user)
            return Job.objects.filter(employer=employer)
        except EmployerProfile.DoesNotExist:
            return Job.objects.none()


class EmployerJobDeleteView(generics.DestroyAPIView):
    """API endpoint for employer to delete a job"""
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        if self.request.user.user_type != 'employer':
            return Job.objects.none()
        
        try:
            employer = EmployerProfile.objects.get(user=self.request.user)
            return Job.objects.filter(employer=employer)
        except EmployerProfile.DoesNotExist:
            return Job.objects.none()


class UpdateApplicationStatusView(APIView):
    """API endpoint for updating application status"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        application = get_object_or_404(
            JobApplication.objects.select_related('job', 'applicant'),
            id=pk
        )
        
        # Check permission
        if request.user.user_type == 'employer':
            if application.job.employer.user != request.user:
                return Response({
                    'success': False,
                    'error': 'Access denied.'
                }, status=status.HTTP_403_FORBIDDEN)
        elif request.user.user_type == 'agency':
            if application.job.agency.user != request.user:
                return Response({
                    'success': False,
                    'error': 'Access denied.'
                }, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({
                'success': False,
                'error': 'Access denied.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = JobApplicationStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        application.status = serializer.validated_data['status']
        if serializer.validated_data.get('notes'):
            application.review_notes = serializer.validated_data['notes']
        application.date_status_changed = timezone.now()
        application.save()
        
        # Notify applicant
        Notification.objects.create(
            user=application.applicant,
            title='Application Status Updated',
            message=f'Your application for "{application.job.title}" has been updated to {application.get_status_display()}.',
            notification_type='application_status',
            link=f'/application/{application.id}/'
        )
        
        return Response({
            'success': True,
            'message': 'Application status updated successfully',
            'application': JobApplicationSerializer(application).data
        })


class EmployerDashboardStatsView(APIView):
    """API endpoint for employer dashboard statistics"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.user_type != 'employer':
            return Response({
                'success': False,
                'error': 'Access denied.'
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
            'total_jobs': jobs.count(),
            'active_jobs': jobs.filter(status='active').count(),
            'pending_jobs': jobs.filter(status='pending').count(),
            'total_applications': applications.count(),
            'shortlisted': applications.filter(status='shortlisted').count(),
            'accepted': applications.filter(status='accepted').count(),
            'rejected': applications.filter(status='rejected').count(),
            'total_views': jobs.aggregate(Sum('views_count'))['views_count__sum'] or 0,
            'is_verified': employer.is_verified,
        }
        return Response(stats)