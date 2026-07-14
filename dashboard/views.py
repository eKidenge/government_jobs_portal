from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum, Q
from django.utils import timezone
from apps.jobs.models import Job, JobApplication
from apps.payments.models import Payment, UserPaymentAccess
from apps.accounts.models import User, UserProfile
from apps.jobs.forms import JobSearchForm

@login_required
def citizen_dashboard(request):
    user = request.user
    if user.user_type != 'citizen':
        messages.error(request, 'Access denied. This is for citizens only.')
        return redirect('home')
    
    # Get user's applications
    applications = JobApplication.objects.filter(applicant=user).select_related('job')
    
    # Get user's profile
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    # Get payment status
    try:
        payment_access = UserPaymentAccess.objects.get(user=user)
        has_payment_access = payment_access.can_apply()
    except UserPaymentAccess.DoesNotExist:
        has_payment_access = False
    
    context = {
        'user': user,
        'profile': profile,
        'applications': applications,
        'applications_count': applications.count(),
        'has_payment_access': has_payment_access,
        'total_applications_used': payment_access.applications_used if has_payment_access else 0,
        'recent_applications': applications[:5],
        'status_counts': {
            'submitted': applications.filter(status='submitted').count(),
            'under_review': applications.filter(status='under_review').count(),
            'shortlisted': applications.filter(status='shortlisted').count(),
            'interview_scheduled': applications.filter(status='interview_scheduled').count(),
            'accepted': applications.filter(status='accepted').count(),
            'rejected': applications.filter(status='rejected').count(),
        }
    }
    
    return render(request, 'dashboard/citizen_dashboard.html', context)

@login_required
def employer_dashboard(request):
    user = request.user
    if user.user_type != 'employer':
        messages.error(request, 'Access denied. This is for employers only.')
        return redirect('home')
    
    try:
        employer = user.employer_profile
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Please complete your employer profile first.')
        return redirect('employer_setup')
    
    jobs = Job.objects.filter(employer=employer)
    applications = JobApplication.objects.filter(job__employer=employer)
    
    context = {
        'employer': employer,
        'jobs': jobs,
        'jobs_count': jobs.count(),
        'active_jobs': jobs.filter(status='active').count(),
        'total_applications': applications.count(),
        'recent_applications': applications.order_by('-date_applied')[:10],
    }
    
    return render(request, 'dashboard/employer_dashboard.html', context)

@login_required
def agency_dashboard(request):
    user = request.user
    if user.user_type != 'agency':
        messages.error(request, 'Access denied. This is for recruitment agencies only.')
        return redirect('home')
    
    try:
        agency = user.agency_profile
    except RecruitmentAgency.DoesNotExist:
        messages.error(request, 'Please complete your agency profile first.')
        return redirect('agency_setup')
    
    jobs = Job.objects.filter(agency=agency)
    applications = JobApplication.objects.filter(job__agency=agency)
    
    context = {
        'agency': agency,
        'jobs': jobs,
        'jobs_count': jobs.count(),
        'active_jobs': jobs.filter(status='active').count(),
        'total_applications': applications.count(),
        'recent_applications': applications.order_by('-date_applied')[:10],
    }
    
    return render(request, 'dashboard/agency_dashboard.html', context)

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')
    
    # Get all statistics
    context = {
        'total_users': User.objects.count(),
        'total_citizens': User.objects.filter(user_type='citizen').count(),
        'total_employers': User.objects.filter(user_type='employer').count(),
        'total_agencies': User.objects.filter(user_type='agency').count(),
        'pending_users': User.objects.filter(status='pending').count(),
        'total_jobs': Job.objects.count(),
        'active_jobs': Job.objects.filter(status='active').count(),
        'pending_jobs': Job.objects.filter(status='pending').count(),
        'total_applications': JobApplication.objects.count(),
        'total_payments': Payment.objects.filter(status='completed').count(),
        'total_revenue': Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0,
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)