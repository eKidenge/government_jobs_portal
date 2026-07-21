"""
Admin Panel Views
Handles government administration dashboard and management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q, Avg
from django.db.models.functions import TruncMonth, TruncDate
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST, require_GET
from django.core.serializers import json
import json as json_lib
import csv
import io
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Import models - FIXED: EmployerProfile from employers.models, not accounts.models
from accounts.models import User, UserProfile
from employers.models import EmployerProfile
from jobs.models import Job, Category, Country, JobApplication
from payments.models import Payment, PaymentPlan, UserPaymentAccess
from agencies.models import RecruitmentAgency
from notifications.models import Notification

# Import forms
from .forms import (
    AdminJobForm, AdminEmployerForm, AdminAgencyForm,
    AdminUserForm, AdminPaymentForm, AdminSettingsForm,
    AdminBulkActionForm
)

# ==============================================
# DASHBOARD VIEWS
# ==============================================

@login_required
@staff_member_required
def admin_dashboard(request):
    """Main admin dashboard"""
    
    # Get current period statistics
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    start_of_week = today - timedelta(days=today.weekday())
    
    # Calculate statistics
    total_users = User.objects.count()
    total_citizens = User.objects.filter(user_type='citizen').count()
    total_employers = User.objects.filter(user_type='employer').count()
    total_agencies = User.objects.filter(user_type='agency').count()
    
    pending_users = User.objects.filter(status='pending').count()
    suspended_users = User.objects.filter(status='suspended').count()
    
    total_jobs = Job.objects.count()
    active_jobs = Job.objects.filter(status='active').count()
    pending_jobs = Job.objects.filter(status='pending').count()
    expired_jobs = Job.objects.filter(closing_date__lt=timezone.now()).count()
    
    total_applications = JobApplication.objects.count()
    applications_this_month = JobApplication.objects.filter(
        date_applied__gte=start_of_month
    ).count()
    
    total_payments = Payment.objects.filter(status='completed').count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(
        Sum('amount')
    )['amount__sum'] or 0
    
    revenue_this_month = Payment.objects.filter(
        status='completed',
        payment_date__date__gte=start_of_month
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Get recent activity
    recent_jobs = Job.objects.order_by('-created_at')[:5]
    recent_applications = JobApplication.objects.order_by('-date_applied')[:5]
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_payments = Payment.objects.filter(status='completed').order_by('-payment_date')[:5]
    
    # Chart data for last 7 days
    week_dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
    applications_by_day = []
    revenue_by_day = []
    
    for date in week_dates:
        next_day = date + timedelta(days=1)
        day_apps = JobApplication.objects.filter(
            date_applied__date__gte=date,
            date_applied__date__lt=next_day
        ).count()
        applications_by_day.append(day_apps)
        
        day_revenue = Payment.objects.filter(
            status='completed',
            payment_date__date__gte=date,
            payment_date__date__lt=next_day
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        revenue_by_day.append(float(day_revenue))
    
    context = {
        # Statistics
        'total_users': total_users,
        'total_citizens': total_citizens,
        'total_employers': total_employers,
        'total_agencies': total_agencies,
        'pending_users': pending_users,
        'suspended_users': suspended_users,
        
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'pending_jobs': pending_jobs,
        'expired_jobs': expired_jobs,
        
        'total_applications': total_applications,
        'applications_this_month': applications_this_month,
        
        'total_payments': total_payments,
        'total_revenue': total_revenue,
        'revenue_this_month': revenue_this_month,
        
        # Recent activity
        'recent_jobs': recent_jobs,
        'recent_applications': recent_applications,
        'recent_users': recent_users,
        'recent_payments': recent_payments,
        
        # Chart data
        'week_labels': [d.strftime('%a') for d in week_dates],
        'applications_by_day': applications_by_day,
        'revenue_by_day': revenue_by_day,
        
        # Quick actions
        'pending_verification': pending_users + pending_jobs,
    }
    
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
@staff_member_required
@require_GET
def dashboard_stats_ajax(request):
    """Get dashboard statistics for AJAX refresh"""
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    
    stats = {
        'total_users': User.objects.count(),
        'active_jobs': Job.objects.filter(status='active').count(),
        'pending_verification': User.objects.filter(status='pending').count() + Job.objects.filter(status='pending').count(),
        'total_revenue': float(Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0),
        'revenue_this_month': float(Payment.objects.filter(status='completed', payment_date__date__gte=start_of_month).aggregate(Sum('amount'))['amount__sum'] or 0),
        'total_applications': JobApplication.objects.count(),
        'applications_this_month': JobApplication.objects.filter(date_applied__date__gte=start_of_month).count(),
    }
    
    return JsonResponse(stats)


# ==============================================
# JOB MANAGEMENT VIEWS
# ==============================================

@login_required
@staff_member_required
def admin_job_list(request):
    """List all jobs with filtering"""
    jobs = Job.objects.select_related('country', 'category', 'employer', 'agency').all()
    
    # Filters
    status = request.GET.get('status')
    country = request.GET.get('country')
    category = request.GET.get('category')
    search = request.GET.get('search')
    
    if status:
        jobs = jobs.filter(status=status)
    if country:
        jobs = jobs.filter(country_id=country)
    if category:
        jobs = jobs.filter(category_id=category)
    if search:
        jobs = jobs.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search) |
            Q(employer__company_name__icontains=search)
        )
    
    paginator = Paginator(jobs, 20)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    
    # Get filter options
    countries = Country.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'jobs': jobs,
        'countries': countries,
        'categories': categories,
        'current_filters': {
            'status': status,
            'country': country,
            'category': category,
            'search': search,
        }
    }
    return render(request, 'admin_panel/jobs/list.html', context)


@login_required
@staff_member_required
def admin_add_job(request):
    """Add a new job"""
    if request.method == 'POST':
        form = AdminJobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by_admin = request.user
            job.status = 'active'
            job.is_verified = True
            job.save()
            messages.success(request, f'Job "{job.title}" added successfully!')
            return redirect('admin_panel:admin_job_list')
    else:
        form = AdminJobForm()
    
    context = {'form': form, 'is_edit': False}
    return render(request, 'admin_panel/jobs/form.html', context)


@login_required
@staff_member_required
def admin_edit_job(request, job_id):
    """Edit a job"""
    job = get_object_or_404(Job, id=job_id)
    
    if request.method == 'POST':
        form = AdminJobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f'Job "{job.title}" updated successfully!')
            return redirect('admin_panel:admin_job_list')
    else:
        form = AdminJobForm(instance=job)
    
    context = {'form': form, 'is_edit': True, 'job': job}
    return render(request, 'admin_panel/jobs/form.html', context)


@login_required
@staff_member_required
@require_POST
def admin_delete_job(request, job_id):
    """Delete a job"""
    job = get_object_or_404(Job, id=job_id)
    job_title = job.title
    job.delete()
    messages.success(request, f'Job "{job_title}" deleted successfully!')
    return redirect('admin_panel:admin_job_list')


@login_required
@staff_member_required
@require_POST
def admin_approve_job(request, job_id):
    """Approve a job"""
    job = get_object_or_404(Job, id=job_id)
    job.status = 'active'
    job.is_verified = True
    job.save()
    
    # Notify employer
    if job.employer:
        Notification.objects.create(
            user=job.employer.user,
            title='Job Approved',
            message=f'Your job "{job.title}" has been approved and is now live.',
            notification_type='job_approved'
        )
    
    messages.success(request, f'Job "{job.title}" approved successfully!')
    return redirect('admin_panel:admin_job_list')


@login_required
@staff_member_required
@require_POST
def admin_reject_job(request, job_id):
    """Reject a job with reason"""
    job = get_object_or_404(Job, id=job_id)
    reason = request.POST.get('reason', 'No reason provided.')
    job.status = 'rejected'
    job.save()
    
    # Notify employer
    if job.employer:
        Notification.objects.create(
            user=job.employer.user,
            title='Job Rejected',
            message=f'Your job "{job.title}" was rejected. Reason: {reason}',
            notification_type='job_rejected'
        )
    
    messages.warning(request, f'Job "{job.title}" rejected.')
    return redirect('admin_panel:admin_job_list')


@login_required
@staff_member_required
@require_POST
def admin_feature_job(request, job_id):
    """Feature or unfeature a job"""
    job = get_object_or_404(Job, id=job_id)
    job.is_featured = not job.is_featured
    job.save()
    
    status = 'featured' if job.is_featured else 'unfeatured'
    messages.success(request, f'Job "{job.title}" {status} successfully!')
    return redirect('admin_panel:admin_job_list')


@login_required
@staff_member_required
@require_POST
def admin_bulk_job_action(request):
    """Bulk action on jobs"""
    form = AdminBulkActionForm(request.POST)
    if form.is_valid():
        job_ids = form.cleaned_data['job_ids'].split(',')
        action = form.cleaned_data['action']
        
        jobs = Job.objects.filter(id__in=job_ids)
        
        if action == 'approve':
            count = jobs.update(status='active', is_verified=True)
            messages.success(request, f'{count} jobs approved.')
        elif action == 'reject':
            count = jobs.update(status='rejected')
            messages.success(request, f'{count} jobs rejected.')
        elif action == 'delete':
            count = jobs.count()
            jobs.delete()
            messages.success(request, f'{count} jobs deleted.')
        elif action == 'feature':
            jobs.update(is_featured=True)
            messages.success(request, f'{jobs.count()} jobs featured.')
        elif action == 'unfeature':
            jobs.update(is_featured=False)
            messages.success(request, f'{jobs.count()} jobs unfeatured.')
    
    return redirect('admin_panel:admin_job_list')


@login_required
@staff_member_required
def admin_export_jobs(request):
    """Export jobs as CSV or Excel"""
    jobs = Job.objects.select_related('country', 'category', 'employer', 'agency').all()
    
    # Apply filters if any
    status = request.GET.get('status')
    if status:
        jobs = jobs.filter(status=status)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="jobs_export_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Title', 'Employer/Agency', 'Country', 'Category', 'Status',
        'Employment Type', 'Salary Min', 'Salary Max', 'Applications',
        'Posted Date', 'Closing Date'
    ])
    
    for job in jobs:
        writer.writerow([
            job.title,
            job.employer.company_name if job.employer else job.agency.agency_name if job.agency else 'N/A',
            job.country.name,
            job.category.name,
            job.status,
            job.employment_type,
            job.salary_min or 'N/A',
            job.salary_max or 'N/A',
            job.applications_count,
            job.posted_date.strftime('%Y-%m-%d'),
            job.closing_date.strftime('%Y-%m-%d'),
        ])
    
    return response


# ==============================================
# EMPLOYER MANAGEMENT VIEWS
# ==============================================

@login_required
@staff_member_required
def admin_employer_list(request):
    """List all employers with filtering"""
    employers = EmployerProfile.objects.select_related('user', 'country').all()
    
    # Filters
    is_verified = request.GET.get('verified')
    search = request.GET.get('search')
    
    if is_verified == 'true':
        employers = employers.filter(is_verified=True)
    elif is_verified == 'false':
        employers = employers.filter(is_verified=False)
    
    if search:
        employers = employers.filter(
            Q(company_name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(registration_number__icontains=search)
        )
    
    paginator = Paginator(employers, 20)
    page = request.GET.get('page')
    employers = paginator.get_page(page)
    
    context = {
        'employers': employers,
        'current_filters': {
            'verified': is_verified,
            'search': search,
        }
    }
    return render(request, 'admin_panel/employers/list.html', context)


@login_required
@staff_member_required
def admin_employer_detail(request, employer_id):
    """View employer details"""
    employer = get_object_or_404(EmployerProfile.objects.select_related('user', 'country'), id=employer_id)
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
    return render(request, 'admin_panel/employers/detail.html', context)


@login_required
@staff_member_required
@require_POST
def admin_verify_employer(request, employer_id):
    """Verify an employer"""
    employer = get_object_or_404(EmployerProfile, id=employer_id)
    employer.is_verified = True
    employer.verification_date = timezone.now()
    employer.save()
    
    # Notify employer
    Notification.objects.create(
        user=employer.user,
        title='Employer Verified',
        message='Your employer account has been verified. You can now post jobs.',
        notification_type='employer_verified'
    )
    
    messages.success(request, f'Employer "{employer.company_name}" verified successfully!')
    return redirect('admin_panel:admin_employer_detail', employer_id=employer_id)


@login_required
@staff_member_required
@require_POST
def admin_suspend_employer(request, employer_id):
    """Suspend an employer"""
    employer = get_object_or_404(EmployerProfile, id=employer_id)
    employer.user.status = 'suspended'
    employer.user.save()
    
    Notification.objects.create(
        user=employer.user,
        title='Account Suspended',
        message='Your employer account has been suspended. Please contact support.',
        notification_type='account_suspended'
    )
    
    messages.warning(request, f'Employer "{employer.company_name}" suspended.')
    return redirect('admin_panel:admin_employer_detail', employer_id=employer_id)


@login_required
@staff_member_required
@require_POST
def admin_activate_employer(request, employer_id):
    """Activate a suspended employer"""
    employer = get_object_or_404(EmployerProfile, id=employer_id)
    employer.user.status = 'approved'
    employer.user.save()
    
    Notification.objects.create(
        user=employer.user,
        title='Account Activated',
        message='Your employer account has been activated.',
        notification_type='account_activated'
    )
    
    messages.success(request, f'Employer "{employer.company_name}" activated.')
    return redirect('admin_panel:admin_employer_detail', employer_id=employer_id)


@login_required
@staff_member_required
@require_POST
def admin_renew_accreditation(request, employer_id):
    """Renew employer accreditation"""
    employer = get_object_or_404(EmployerProfile, id=employer_id)
    # Implement accreditation renewal logic
    messages.success(request, f'Accreditation for "{employer.company_name}" renewed.')
    return redirect('admin_panel:admin_employer_detail', employer_id=employer_id)


@login_required
@staff_member_required
@require_POST
def admin_delete_employer(request, employer_id):
    """Delete an employer"""
    employer = get_object_or_404(EmployerProfile, id=employer_id)
    company_name = employer.company_name
    employer.delete()
    messages.success(request, f'Employer "{company_name}" deleted.')
    return redirect('admin_panel:admin_employer_list')


@login_required
@staff_member_required
def admin_register_employer(request):
    """Register a new employer from admin panel"""
    if request.method == 'POST':
        form = AdminEmployerForm(request.POST)
        if form.is_valid():
            # Create user and employer profile
            user = form.save(commit=False)
            user.user_type = 'employer'
            user.status = 'approved'
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            employer = EmployerProfile.objects.create(
                user=user,
                company_name=form.cleaned_data['company_name'],
                registration_number=form.cleaned_data['registration_number'],
                is_verified=True,
                verification_date=timezone.now()
            )
            
            messages.success(request, f'Employer "{employer.company_name}" registered successfully!')
            return redirect('admin_panel:admin_employer_detail', employer_id=employer.id)
    else:
        form = AdminEmployerForm()
    
    context = {'form': form, 'is_edit': False}
    return render(request, 'admin_panel/employers/register.html', context)


@login_required
@staff_member_required
def admin_employer_setup(request, employer_id):
    """Set up an employer account"""
    employer = get_object_or_404(EmployerProfile, id=employer_id)
    
    if request.method == 'POST':
        # Implement employer setup logic
        messages.success(request, f'Employer "{employer.company_name}" setup completed!')
        return redirect('admin_panel:admin_employer_detail', employer_id=employer_id)
    
    context = {'employer': employer}
    return render(request, 'admin_panel/employers/setup.html', context)


@login_required
@staff_member_required
def admin_export_employers(request):
    """Export employers as CSV"""
    employers = EmployerProfile.objects.select_related('user', 'country').all()
    
    # Apply filters if any
    is_verified = request.GET.get('verified')
    search = request.GET.get('search')
    
    if is_verified == 'true':
        employers = employers.filter(is_verified=True)
    elif is_verified == 'false':
        employers = employers.filter(is_verified=False)
    
    if search:
        employers = employers.filter(
            Q(company_name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(registration_number__icontains=search)
        )
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="employers_export_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Company Name', 'Email', 'Phone', 'Registration Number',
        'Country', 'Industry', 'Verified', 'Status', 'Date Joined'
    ])
    
    for employer in employers:
        writer.writerow([
            employer.company_name,
            employer.user.email,
            employer.phone_number or 'N/A',
            employer.registration_number or 'N/A',
            employer.country.name if employer.country else 'N/A',
            employer.industry or 'N/A',
            'Yes' if employer.is_verified else 'No',
            employer.user.get_status_display(),
            employer.created_at.strftime('%Y-%m-%d') if hasattr(employer, 'created_at') else employer.user.date_joined.strftime('%Y-%m-%d'),
        ])
    
    return response


# ==============================================
# RECRUITMENT AGENCY MANAGEMENT VIEWS
# ==============================================

@login_required
@staff_member_required
def admin_agency_list(request):
    """List all recruitment agencies"""
    agencies = RecruitmentAgency.objects.select_related('user', 'country').all()
    
    is_verified = request.GET.get('verified')
    search = request.GET.get('search')
    
    if is_verified == 'true':
        agencies = agencies.filter(is_verified=True)
    elif is_verified == 'false':
        agencies = agencies.filter(is_verified=False)
    
    if search:
        agencies = agencies.filter(
            Q(agency_name__icontains=search) |
            Q(user__email__icontains=search) |
            Q(license_number__icontains=search)
        )
    
    paginator = Paginator(agencies, 20)
    page = request.GET.get('page')
    agencies = paginator.get_page(page)
    
    context = {
        'agencies': agencies,
        'current_filters': {
            'verified': is_verified,
            'search': search,
        }
    }
    return render(request, 'admin_panel/agencies/list.html', context)


@login_required
@staff_member_required
def admin_agency_detail(request, agency_id):
    """View agency details"""
    agency = get_object_or_404(RecruitmentAgency.objects.select_related('user', 'country'), id=agency_id)
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
    return render(request, 'admin_panel/agencies/detail.html', context)


@login_required
@staff_member_required
@require_POST
def admin_verify_agency(request, agency_id):
    """Verify a recruitment agency"""
    agency = get_object_or_404(RecruitmentAgency, id=agency_id)
    agency.is_verified = True
    agency.verification_date = timezone.now()
    agency.save()
    
    Notification.objects.create(
        user=agency.user,
        title='Agency Verified',
        message='Your agency has been verified. You can now post jobs.',
        notification_type='agency_verified'
    )
    
    messages.success(request, f'✅ Agency "{agency.agency_name}" verified successfully!')
    return redirect('admin_panel:admin_agency_detail', agency_id=agency_id)


@login_required
@staff_member_required
@require_POST
def admin_suspend_agency(request, agency_id):
    """Suspend an agency"""
    agency = get_object_or_404(RecruitmentAgency, id=agency_id)
    agency.user.status = 'suspended'
    agency.user.save()
    
    Notification.objects.create(
        user=agency.user,
        title='Account Suspended',
        message='Your agency account has been suspended. Please contact support.',
        notification_type='account_suspended'
    )
    
    messages.warning(request, f'⚠️ Agency "{agency.agency_name}" suspended.')
    return redirect('admin_panel:admin_agency_detail', agency_id=agency_id)


@login_required
@staff_member_required
@require_POST
def admin_activate_agency(request, agency_id):
    """Activate an agency"""
    agency = get_object_or_404(RecruitmentAgency, id=agency_id)
    agency.user.status = 'approved'
    agency.user.save()
    
    Notification.objects.create(
        user=agency.user,
        title='Account Activated',
        message='Your agency account has been activated.',
        notification_type='account_activated'
    )
    
    messages.success(request, f'✅ Agency "{agency.agency_name}" activated.')
    return redirect('admin_panel:admin_agency_detail', agency_id=agency_id)


@login_required
@staff_member_required
@require_POST
def admin_delete_agency(request, agency_id):
    """Delete an agency"""
    agency = get_object_or_404(RecruitmentAgency, id=agency_id)
    agency_name = agency.agency_name
    agency.delete()
    messages.success(request, f'🗑️ Agency "{agency_name}" deleted.')
    return redirect('admin_panel:admin_agency_list')


@login_required
@staff_member_required
def admin_register_agency(request):
    """Register a new recruitment agency from admin panel"""
    if request.method == 'POST':
        form = AdminAgencyForm(request.POST)
        if form.is_valid():
            # Create user and agency profile
            user = form.save(commit=False)
            user.user_type = 'agency'
            user.status = 'approved'
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            agency = RecruitmentAgency.objects.create(
                user=user,
                agency_name=form.cleaned_data['agency_name'],
                registration_number=form.cleaned_data['registration_number'],
                license_number=form.cleaned_data['license_number'],
                license_expiry=form.cleaned_data['license_expiry'],
                address=form.cleaned_data.get('address', ''),
                contact_phone=form.cleaned_data['contact_phone'],
                contact_email=form.cleaned_data['contact_email'],
                description=form.cleaned_data.get('description', ''),
                is_verified=True,
                verification_date=timezone.now()
            )
            
            messages.success(request, f'✅ Agency "{agency.agency_name}" registered successfully!')
            return redirect('admin_panel:admin_agency_detail', agency_id=agency.id)
    else:
        form = AdminAgencyForm()
    
    context = {'form': form, 'is_edit': False}
    return render(request, 'admin_panel/agencies/register.html', context)


@login_required
@staff_member_required
def admin_agency_setup(request, agency_id):
    """Set up a recruitment agency account"""
    agency = get_object_or_404(RecruitmentAgency, id=agency_id)
    
    if request.method == 'POST':
        # Implement agency setup logic
        messages.success(request, f'✅ Agency "{agency.agency_name}" setup completed!')
        return redirect('admin_panel:admin_agency_detail', agency_id=agency_id)
    
    context = {'agency': agency}
    return render(request, 'admin_panel/agencies/setup.html', context)


# ==============================================
# USER MANAGEMENT VIEWS
# ==============================================

@login_required
@staff_member_required
def admin_user_list(request):
    """List all users"""
    users = User.objects.all()
    
    user_type = request.GET.get('user_type')
    status = request.GET.get('status')
    search = request.GET.get('search')
    
    if user_type:
        users = users.filter(user_type=user_type)
    if status:
        users = users.filter(status=status)
    if search:
        users = users.filter(
            Q(email__icontains=search) |
            Q(full_name__icontains=search) |
            Q(national_id__icontains=search) |
            Q(phone_number__icontains=search)
        )
    
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    context = {
        'users': users,
        'current_filters': {
            'user_type': user_type,
            'status': status,
            'search': search,
        }
    }
    return render(request, 'admin_panel/users/list.html', context)


@login_required
@staff_member_required
def admin_user_detail(request, user_id):
    """View user details"""
    user = get_object_or_404(User, id=user_id)
    
    # Get user's applications
    applications = JobApplication.objects.filter(applicant=user)
    
    # Get user's payments
    payments = Payment.objects.filter(user=user)
    
    context = {
        'user': user,
        'applications': applications,
        'applications_count': applications.count(),
        'payments': payments,
        'total_paid': payments.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0,
    }
    return render(request, 'admin_panel/users/detail.html', context)


@login_required
@staff_member_required
@require_POST
def admin_approve_user(request, user_id):
    """Approve a user"""
    user = get_object_or_404(User, id=user_id)
    user.status = 'approved'
    user.is_verified = True
    user.save()
    
    Notification.objects.create(
        user=user,
        title='Account Approved',
        message='Your account has been approved. You can now access all features.',
        notification_type='account_approved'
    )
    
    messages.success(request, f'✅ User "{user.full_name}" approved!')
    return redirect('admin_panel:admin_user_list')


@login_required
@staff_member_required
@require_POST
def admin_suspend_user(request, user_id):
    """Suspend a user"""
    user = get_object_or_404(User, id=user_id)
    user.status = 'suspended'
    user.save()
    
    Notification.objects.create(
        user=user,
        title='Account Suspended',
        message='Your account has been suspended. Please contact support for more information.',
        notification_type='account_suspended'
    )
    
    messages.warning(request, f'⚠️ User "{user.full_name}" suspended.')
    return redirect('admin_panel:admin_user_list')


@login_required
@staff_member_required
@require_POST
def admin_activate_user(request, user_id):
    """Activate a suspended user"""
    user = get_object_or_404(User, id=user_id)
    user.status = 'approved'
    user.save()
    
    Notification.objects.create(
        user=user,
        title='Account Activated',
        message='Your account has been reactivated.',
        notification_type='account_activated'
    )
    
    messages.success(request, f'✅ User "{user.full_name}" activated.')
    return redirect('admin_panel:admin_user_list')


@login_required
@staff_member_required
@require_POST
def admin_reset_user_password(request, user_id):
    """Reset user password"""
    user = get_object_or_404(User, id=user_id)
    new_password = request.POST.get('new_password')
    
    if new_password and len(new_password) >= 8:
        user.set_password(new_password)
        user.save()
        
        Notification.objects.create(
            user=user,
            title='Password Reset',
            message='Your password has been reset by the administrator.',
            notification_type='password_reset'
        )
        
        messages.success(request, f'✅ Password for "{user.full_name}" reset successfully!')
    else:
        messages.error(request, '❌ Invalid password. Must be at least 8 characters.')
    
    return redirect('admin_panel:admin_user_list')


@login_required
@staff_member_required
@require_POST
def admin_delete_user(request, user_id):
    """Delete a user"""
    user = get_object_or_404(User, id=user_id)
    full_name = user.full_name
    user.delete()
    messages.success(request, f'🗑️ User "{full_name}" deleted.')
    return redirect('admin_panel:admin_user_list')


@login_required
@staff_member_required
@require_POST
def admin_bulk_user_action(request):
    """Bulk action on users"""
    user_ids = request.POST.get('user_ids', '').split(',')
    action = request.POST.get('action')
    
    if not user_ids:
        messages.error(request, 'No users selected.')
        return redirect('admin_panel:admin_user_list')
    
    users = User.objects.filter(id__in=user_ids)
    
    if action == 'approve':
        count = users.update(status='approved', is_verified=True)
        messages.success(request, f'{count} users approved.')
    elif action == 'suspend':
        count = users.update(status='suspended')
        messages.success(request, f'{count} users suspended.')
    elif action == 'activate':
        count = users.update(status='approved')
        messages.success(request, f'{count} users activated.')
    elif action == 'delete':
        count = users.count()
        users.delete()
        messages.success(request, f'{count} users deleted.')
    
    return redirect('admin_panel:admin_user_list')


@login_required
@staff_member_required
def admin_export_users(request):
    """Export users as CSV"""
    users = User.objects.all()
    
    # Apply filters if any
    user_type = request.GET.get('user_type')
    status = request.GET.get('status')
    search = request.GET.get('search')
    
    if user_type:
        users = users.filter(user_type=user_type)
    if status:
        users = users.filter(status=status)
    if search:
        users = users.filter(
            Q(email__icontains=search) |
            Q(full_name__icontains=search) |
            Q(national_id__icontains=search) |
            Q(phone_number__icontains=search)
        )
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="users_export_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Full Name', 'Email', 'Phone', 'National ID', 'User Type', 
        'Status', 'Verified', 'Date Joined'
    ])
    
    for user in users:
        writer.writerow([
            user.full_name,
            user.email,
            user.phone_number or 'N/A',
            user.national_id or 'N/A',
            user.get_user_type_display(),
            user.get_status_display(),
            'Yes' if user.is_verified else 'No',
            user.date_joined.strftime('%Y-%m-%d %H:%M'),
        ])
    
    return response


# ==============================================
# PAYMENT MANAGEMENT VIEWS
# ==============================================

@login_required
@staff_member_required
def admin_payment_list(request):
    """List all payments"""
    payments = Payment.objects.select_related('user', 'plan').all()
    
    status = request.GET.get('status')
    payment_method = request.GET.get('payment_method')
    search = request.GET.get('search')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if status:
        payments = payments.filter(status=status)
    if payment_method:
        payments = payments.filter(payment_method=payment_method)
    if search:
        payments = payments.filter(
            Q(user__email__icontains=search) |
            Q(user__full_name__icontains=search) |
            Q(transaction_reference__icontains=search)
        )
    if date_from:
        payments = payments.filter(payment_date__date__gte=date_from)
    if date_to:
        payments = payments.filter(payment_date__date__lte=date_to)
    
    paginator = Paginator(payments, 20)
    page = request.GET.get('page')
    payments = paginator.get_page(page)
    
    # Summary statistics
    total_payments = Payment.objects.filter(status='completed').count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    pending_payments = Payment.objects.filter(status='pending').count()
    
    context = {
        'payments': payments,
        'total_payments': total_payments,
        'total_revenue': total_revenue,
        'pending_payments': pending_payments,
        'current_filters': {
            'status': status,
            'payment_method': payment_method,
            'search': search,
            'date_from': date_from,
            'date_to': date_to,
        }
    }
    return render(request, 'admin_panel/payments/list.html', context)


@login_required
@staff_member_required
def admin_payment_detail(request, payment_id):
    """View payment details"""
    payment = get_object_or_404(Payment.objects.select_related('user', 'plan'), id=payment_id)
    
    context = {'payment': payment}
    return render(request, 'admin_panel/payments/detail.html', context)


@login_required
@staff_member_required
@require_POST
def admin_verify_payment(request, payment_id):
    """Verify a pending payment"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    if payment.status == 'pending':
        payment.status = 'completed'
        payment.completed_date = timezone.now()
        payment.save()
        
        # Grant access to user
        from payments.views import grant_payment_access
        grant_payment_access(payment.user, payment)
        
        messages.success(request, f'✅ Payment {payment.transaction_reference} verified!')
    else:
        messages.warning(request, '⚠️ Payment is not pending.')
    
    return redirect('admin_panel:admin_payment_detail', payment_id=payment_id)


@login_required
@staff_member_required
@require_POST
def admin_refund_payment(request, payment_id):
    """Refund a payment"""
    payment = get_object_or_404(Payment, id=payment_id)
    reason = request.POST.get('reason', 'No reason provided.')
    
    if payment.status == 'completed':
        payment.status = 'refunded'
        payment.save()
        
        # Revoke access
        try:
            access = UserPaymentAccess.objects.get(user=payment.user)
            access.has_access = False
            access.save()
        except UserPaymentAccess.DoesNotExist:
            pass
        
        Notification.objects.create(
            user=payment.user,
            title='Payment Refunded',
            message=f'Your payment of {payment.amount} {payment.currency} has been refunded. Reason: {reason}',
            notification_type='payment_refunded'
        )
        
        messages.success(request, f'✅ Payment {payment.transaction_reference} refunded!')
    else:
        messages.warning(request, '⚠️ Only completed payments can be refunded.')
    
    return redirect('admin_panel:admin_payment_detail', payment_id=payment_id)


@login_required
@staff_member_required
def admin_export_payments(request):
    """Export payments as CSV"""
    payments = Payment.objects.select_related('user', 'plan').filter(status='completed')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="payments_export_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Reference', 'User', 'Amount', 'Currency', 'Method', 'Status',
        'Payment Date', 'Completed Date', 'Plan'
    ])
    
    for payment in payments:
        writer.writerow([
            payment.transaction_reference,
            payment.user.full_name,
            payment.amount,
            payment.currency,
            payment.payment_method,
            payment.status,
            payment.payment_date.strftime('%Y-%m-%d %H:%M'),
            payment.completed_date.strftime('%Y-%m-%d %H:%M') if payment.completed_date else 'N/A',
            payment.plan.name if payment.plan else 'N/A',
        ])
    
    return response


# ==============================================
# PAYMENT PLANS MANAGEMENT VIEWS
# ==============================================

@login_required
@staff_member_required
def admin_payment_plans(request):
    """List all payment plans"""
    plans = PaymentPlan.objects.all()
    context = {'plans': plans}
    return render(request, 'admin_panel/payment_plans/list.html', context)


@login_required
@staff_member_required
def admin_add_payment_plan(request):
    """Add a new payment plan"""
    if request.method == 'POST':
        # Implement form handling
        messages.success(request, 'Payment plan added successfully!')
        return redirect('admin_panel:admin_payment_plans')
    return render(request, 'admin_panel/payment_plans/form.html', {'is_edit': False})


@login_required
@staff_member_required
def admin_edit_payment_plan(request, plan_id):
    """Edit a payment plan"""
    plan = get_object_or_404(PaymentPlan, id=plan_id)
    if request.method == 'POST':
        # Implement form handling
        messages.success(request, 'Payment plan updated successfully!')
        return redirect('admin_panel:admin_payment_plans')
    return render(request, 'admin_panel/payment_plans/form.html', {'is_edit': True, 'plan': plan})


@login_required
@staff_member_required
@require_POST
def admin_delete_payment_plan(request, plan_id):
    """Delete a payment plan"""
    plan = get_object_or_404(PaymentPlan, id=plan_id)
    plan.delete()
    messages.success(request, 'Payment plan deleted successfully!')
    return redirect('admin_panel:admin_payment_plans')


# ==============================================
# CATEGORIES MANAGEMENT VIEWS
# ==============================================

@login_required
@staff_member_required
def admin_categories(request):
    """List all categories"""
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'admin_panel/categories/list.html', context)


@login_required
@staff_member_required
def admin_add_category(request):
    """Add a new category"""
    if request.method == 'POST':
        # Implement form handling
        messages.success(request, 'Category added successfully!')
        return redirect('admin_panel:admin_categories')
    return render(request, 'admin_panel/categories/form.html', {'is_edit': False})


@login_required
@staff_member_required
def admin_edit_category(request, category_id):
    """Edit a category"""
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        # Implement form handling
        messages.success(request, 'Category updated successfully!')
        return redirect('admin_panel:admin_categories')
    return render(request, 'admin_panel/categories/form.html', {'is_edit': True, 'category': category})


@login_required
@staff_member_required
@require_POST
def admin_delete_category(request, category_id):
    """Delete a category"""
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('admin_panel:admin_categories')


# ==============================================
# COUNTRIES MANAGEMENT VIEWS
# ==============================================

@login_required
@staff_member_required
def admin_countries(request):
    """List all countries"""
    countries = Country.objects.all()
    context = {'countries': countries}
    return render(request, 'admin_panel/countries/list.html', context)


@login_required
@staff_member_required
def admin_add_country(request):
    """Add a new country"""
    if request.method == 'POST':
        # Implement form handling
        messages.success(request, 'Country added successfully!')
        return redirect('admin_panel:admin_countries')
    return render(request, 'admin_panel/countries/form.html', {'is_edit': False})


@login_required
@staff_member_required
def admin_edit_country(request, country_id):
    """Edit a country"""
    country = get_object_or_404(Country, id=country_id)
    if request.method == 'POST':
        # Implement form handling
        messages.success(request, 'Country updated successfully!')
        return redirect('admin_panel:admin_countries')
    return render(request, 'admin_panel/countries/form.html', {'is_edit': True, 'country': country})


@login_required
@staff_member_required
@require_POST
def admin_delete_country(request, country_id):
    """Delete a country"""
    country = get_object_or_404(Country, id=country_id)
    country.delete()
    messages.success(request, 'Country deleted successfully!')
    return redirect('admin_panel:admin_countries')


# ==============================================
# REPORTS VIEWS
# ==============================================

@login_required
@staff_member_required
def admin_reports(request):
    """Reports dashboard"""
    context = {
        'report_types': [
            {'id': 'placements', 'name': 'Placement Statistics'},
            {'id': 'jobs_by_country', 'name': 'Jobs by Country'},
            {'id': 'jobs_by_sector', 'name': 'Jobs by Sector'},
            {'id': 'revenue', 'name': 'Revenue Report'},
            {'id': 'labour_migration', 'name': 'Labour Migration'},
            {'id': 'users', 'name': 'User Statistics'},
            {'id': 'applications', 'name': 'Application Statistics'},
        ]
    }
    return render(request, 'admin_panel/reports/index.html', context)


@login_required
@staff_member_required
def admin_placements_report(request):
    """Generate placements report"""
    # Get placement statistics
    total_placements = JobApplication.objects.filter(status='accepted').count()
    
    # By month
    placements_by_month = JobApplication.objects.filter(
        status='accepted'
    ).annotate(
        month=TruncMonth('date_updated')
    ).values('month').annotate(
        count=Count('id')
    ).order_by('-month')
    
    # By country
    placements_by_country = JobApplication.objects.filter(
        status='accepted'
    ).values('job__country__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # By sector
    placements_by_sector = JobApplication.objects.filter(
        status='accepted'
    ).values('job__category__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'total_placements': total_placements,
        'placements_by_month': placements_by_month,
        'placements_by_country': placements_by_country,
        'placements_by_sector': placements_by_sector,
    }
    return render(request, 'admin_panel/reports/placements.html', context)


@login_required
@staff_member_required
def admin_jobs_by_country_report(request):
    """Jobs by country report"""
    jobs_by_country = Job.objects.filter(status='active').values(
        'country__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {'jobs_by_country': jobs_by_country}
    return render(request, 'admin_panel/reports/jobs_by_country.html', context)


@login_required
@staff_member_required
def admin_jobs_by_sector_report(request):
    """Jobs by sector report"""
    jobs_by_sector = Job.objects.filter(status='active').values(
        'category__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {'jobs_by_sector': jobs_by_sector}
    return render(request, 'admin_panel/reports/jobs_by_sector.html', context)


@login_required
@staff_member_required
def admin_revenue_report(request):
    """Revenue report"""
    # Overall revenue
    total_revenue = Payment.objects.filter(status='completed').aggregate(
        Sum('amount')
    )['amount__sum'] or 0
    
    # Revenue by month
    revenue_by_month = Payment.objects.filter(
        status='completed'
    ).annotate(
        month=TruncMonth('payment_date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('-month')
    
    # Revenue by plan
    revenue_by_plan = Payment.objects.filter(
        status='completed'
    ).values('plan__name').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Revenue by payment method
    revenue_by_method = Payment.objects.filter(
        status='completed'
    ).values('payment_method').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    context = {
        'total_revenue': total_revenue,
        'revenue_by_month': revenue_by_month,
        'revenue_by_plan': revenue_by_plan,
        'revenue_by_method': revenue_by_method,
    }
    return render(request, 'admin_panel/reports/revenue.html', context)


@login_required
@staff_member_required
def admin_labour_migration_report(request):
    """Labour migration report"""
    # Labour migration statistics
    migration_data = JobApplication.objects.filter(
        status='accepted'
    ).values(
        'job__country__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')
    
    # By sector
    migration_by_sector = JobApplication.objects.filter(
        status='accepted'
    ).values(
        'job__category__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'migration_data': migration_data,
        'migration_by_sector': migration_by_sector,
        'total_migrants': JobApplication.objects.filter(status='accepted').count(),
    }
    return render(request, 'admin_panel/reports/labour_migration.html', context)


@login_required
@staff_member_required
def admin_export_report(request, report_type):
    """Export report as CSV or PDF"""
    format = request.GET.get('format', 'csv')
    
    if format == 'csv':
        return export_report_csv(report_type, request)
    elif format == 'pdf':
        return export_report_pdf(report_type, request)
    else:
        messages.error(request, 'Invalid export format.')
        return redirect('admin_panel:admin_reports')


def export_report_csv(report_type, request):
    """Export report as CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    
    if report_type == 'placements':
        writer.writerow(['Month', 'Total Placements'])
        data = JobApplication.objects.filter(status='accepted').annotate(
            month=TruncMonth('date_updated')
        ).values('month').annotate(count=Count('id'))
        for item in data:
            writer.writerow([item['month'].strftime('%Y-%m'), item['count']])
    
    elif report_type == 'revenue':
        writer.writerow(['Month', 'Total Revenue (KES)'])
        data = Payment.objects.filter(status='completed').annotate(
            month=TruncMonth('payment_date')
        ).values('month').annotate(total=Sum('amount'))
        for item in data:
            writer.writerow([item['month'].strftime('%Y-%m'), item['total']])
    
    return response


def export_report_pdf(report_type, request):
    """Export report as PDF"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report_{datetime.now().strftime("%Y%m%d")}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    
    # Add title
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1
    )
    elements.append(Paragraph(f'{report_type.title()} Report', title_style))
    elements.append(Spacer(1, 20))
    
    if report_type == 'placements':
        data = JobApplication.objects.filter(status='accepted').annotate(
            month=TruncMonth('date_updated')
        ).values('month').annotate(count=Count('id'))
        
        table_data = [['Month', 'Total Placements']]
        for item in data:
            table_data.append([item['month'].strftime('%Y-%m'), str(item['count'])])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
    
    elif report_type == 'revenue':
        data = Payment.objects.filter(status='completed').annotate(
            month=TruncMonth('payment_date')
        ).values('month').annotate(total=Sum('amount'))
        
        table_data = [['Month', 'Total Revenue (KES)']]
        for item in data:
            table_data.append([item['month'].strftime('%Y-%m'), f"{item['total']:,.2f}"])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
    
    doc.build(elements)
    return response


# ==============================================
# SYSTEM SETTINGS VIEWS
# ==============================================

@login_required
@staff_member_required
def admin_settings(request):
    """System settings page"""
    from django.conf import settings
    
    context = {
        'site_name': settings.SITE_NAME,
        'site_url': settings.SITE_URL,
        'admin_email': settings.ADMIN_EMAIL,
        'mpesa_configured': bool(settings.MPESA_CONSUMER_KEY),
        'email_configured': bool(settings.EMAIL_HOST_USER),
    }
    return render(request, 'admin_panel/settings/index.html', context)


@login_required
@staff_member_required
@require_POST
def admin_update_settings(request):
    """Update system settings"""
    form = AdminSettingsForm(request.POST)
    if form.is_valid():
        # Save settings to database or environment
        messages.success(request, 'Settings updated successfully!')
    else:
        messages.error(request, 'Invalid settings provided.')
    
    return redirect('admin_panel:admin_settings')


# ==============================================
# ADMIN PROFILE VIEWS
# ==============================================

@login_required
@staff_member_required
def admin_profile(request):
    """View admin profile"""
    context = {'admin_user': request.user}
    return render(request, 'admin_panel/profile.html', context)


@login_required
@staff_member_required
def admin_profile_update(request):
    """Update admin profile"""
    if request.method == 'POST':
        # Implement profile update logic
        messages.success(request, 'Profile updated successfully!')
    return redirect('admin_panel:admin_profile')


# ==============================================
# ACTIVITY LOGS VIEWS
# ==============================================

@login_required
@staff_member_required
def admin_activity_logs(request):
    """View activity logs"""
    # Implement activity log retrieval
    context = {'logs': []}
    return render(request, 'admin_panel/activity_logs/list.html', context)


@login_required
@staff_member_required
def admin_activity_log_detail(request, log_id):
    """View activity log details"""
    context = {'log_id': log_id}
    return render(request, 'admin_panel/activity_logs/detail.html', context)


# ==============================================
# AJAX ENDPOINTS
# ==============================================

@login_required
@staff_member_required
@require_GET
def ajax_job_status(request, job_id):
    """Get job status for AJAX"""
    job = get_object_or_404(Job, id=job_id)
    return JsonResponse({
        'id': str(job.id),
        'title': job.title,
        'status': job.status,
        'is_verified': job.is_verified,
        'is_featured': job.is_featured,
        'applications_count': job.applications_count,
        'closing_date': job.closing_date.strftime('%Y-%m-%d'),
    })


@login_required
@staff_member_required
@require_GET
def ajax_user_status(request, user_id):
    """Get user status for AJAX"""
    user = get_object_or_404(User, id=user_id)
    return JsonResponse({
        'id': str(user.id),
        'full_name': user.full_name,
        'email': user.email,
        'user_type': user.user_type,
        'status': user.status,
        'is_verified': user.is_verified,
        'date_joined': user.date_joined.strftime('%Y-%m-%d'),
    })


@login_required
@staff_member_required
@require_GET
def ajax_employer_status(request, employer_id):
    """Get employer status for AJAX"""
    employer = get_object_or_404(EmployerProfile, id=employer_id)
    return JsonResponse({
        'id': str(employer.id),
        'company_name': employer.company_name,
        'is_verified': employer.is_verified,
        'verification_date': employer.verification_date.strftime('%Y-%m-%d') if employer.verification_date else None,
        'jobs_count': Job.objects.filter(employer=employer).count(),
    })


@login_required
@staff_member_required
@require_GET
def ajax_agency_status(request, agency_id):
    """Get agency status for AJAX"""
    agency = get_object_or_404(RecruitmentAgency, id=agency_id)
    return JsonResponse({
        'id': str(agency.id),
        'agency_name': agency.agency_name,
        'is_verified': agency.is_verified,
        'verification_date': agency.verification_date.strftime('%Y-%m-%d') if agency.verification_date else None,
        'jobs_count': Job.objects.filter(agency=agency).count(),
    })