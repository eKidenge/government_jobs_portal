"""
Employers Views
Handles employer registration, profile management, and dashboard
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET
from datetime import timedelta

from .models import EmployerProfile, EmployerDocument
from .forms import EmployerProfileForm, EmployerDocumentForm
from accounts.models import User
from accounts.forms import EmployerRegistrationForm
from jobs.models import Job, JobApplication, Country
from jobs.forms import JobForm
from notifications.models import Notification


def employer_list(request):
    """List all verified employers"""
    employers = EmployerProfile.objects.filter(
        is_verified=True
    ).select_related('user', 'country').order_by('company_name')
    
    # Search
    search = request.GET.get('search')
    if search:
        employers = employers.filter(
            Q(company_name__icontains=search) |
            Q(description__icontains=search) |
            Q(industry__icontains=search)
        )
    
    # Filter by industry
    industry = request.GET.get('industry')
    if industry:
        employers = employers.filter(industry=industry)
    
    # Filter by country
    country = request.GET.get('country')
    if country:
        employers = employers.filter(country_id=country)
    
    # Annotate with job count
    employers = employers.annotate(
        job_count=Count('jobs', filter=Q(jobs__status='active', jobs__closing_date__gte=timezone.now()))
    )
    
    paginator = Paginator(employers, 12)
    page = request.GET.get('page')
    employers = paginator.get_page(page)
    
    # Get filter options
    industries = EmployerProfile.INDUSTRIES
    countries = Country.objects.filter(is_active=True)
    
    context = {
        'employers': employers,
        'paginator': paginator,
        'industries': industries,
        'countries': countries,
        'current_filters': request.GET,
    }
    return render(request, 'employers/list.html', context)


def employer_detail(request, employer_id):
    """View employer details"""
    employer = get_object_or_404(
        EmployerProfile.objects.select_related('user', 'country'),
        id=employer_id,
        is_verified=True
    )
    
    # Get active jobs
    jobs = Job.objects.filter(
        employer=employer,
        status='active',
        is_verified=True,
        closing_date__gte=timezone.now()
    ).select_related('country', 'category').order_by('-posted_date')
    
    # Get job count
    job_count = jobs.count()
    
    # Get recent jobs (limit to 5)
    recent_jobs = jobs[:5]
    
    context = {
        'employer': employer,
        'jobs': jobs,
        'recent_jobs': recent_jobs,
        'job_count': job_count,
        'total_applications': JobApplication.objects.filter(job__employer=employer).count(),
    }
    return render(request, 'employers/detail.html', context)


def employer_register(request):
    """Employer registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = EmployerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'employer'
            user.status = 'pending'
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Create employer profile (will be completed in setup)
            EmployerProfile.objects.create(
                user=user,
                company_name=form.cleaned_data.get('company_name', ''),
                contact_email=user.email,
                contact_phone=user.phone_number,
            )
            
            messages.success(request, 'Employer account created! Please complete your profile setup.')
            return redirect('employer_setup')
    else:
        form = EmployerRegistrationForm()
    
    context = {'form': form}
    return render(request, 'employers/register.html', context)


@login_required
def employer_setup(request):
    """Complete employer profile setup"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied. This is for employers only.')
        return redirect('home')
    
    try:
        employer = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        employer = EmployerProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = EmployerProfileForm(request.POST, request.FILES, instance=employer)
        if form.is_valid():
            employer = form.save(commit=False)
            employer.user = request.user
            
            # Handle logo upload
            if 'logo' in request.FILES:
                employer.logo = request.FILES['logo']
            
            employer.save()
            
            messages.success(request, 'Employer profile completed successfully!')
            return redirect('employer_dashboard')
    else:
        form = EmployerProfileForm(instance=employer)
    
    context = {
        'form': form,
        'employer': employer,
    }
    return render(request, 'employers/setup.html', context)


@login_required
def employer_verification(request):
    """Upload verification documents"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied. This is for employers only.')
        return redirect('home')
    
    try:
        employer = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Please complete your employer profile first.')
        return redirect('employer_setup')
    
    if request.method == 'POST':
        form = EmployerDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.employer = employer
            doc.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('employer_verification')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmployerDocumentForm()
    
    documents = EmployerDocument.objects.filter(employer=employer)
    
    context = {
        'employer': employer,
        'documents': documents,
        'form': form,
        'document_types': EmployerDocument.DOCUMENT_TYPES,
    }
    return render(request, 'employers/verification.html', context)


@login_required
def employer_profile_update(request):
    """Update employer profile"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied. This is for employers only.')
        return redirect('home')
    
    try:
        employer = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Please complete your employer profile first.')
        return redirect('employer_setup')
    
    if request.method == 'POST':
        form = EmployerProfileForm(request.POST, request.FILES, instance=employer)
        if form.is_valid():
            employer = form.save()
            
            # Update user info
            user = request.user
            if request.POST.get('full_name'):
                user.full_name = request.POST.get('full_name')
            if request.POST.get('phone_number'):
                user.phone_number = request.POST.get('phone_number')
            user.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('employer_dashboard')
    else:
        form = EmployerProfileForm(instance=employer)
    
    context = {
        'form': form,
        'employer': employer,
        'user': request.user,
    }
    return render(request, 'employers/profile_update.html', context)


@login_required
@require_POST
def employer_logo_upload(request):
    """Upload employer logo via AJAX"""
    if request.user.user_type != 'employer':
        return JsonResponse({'success': False, 'error': 'Access denied.'})
    
    try:
        employer = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Employer profile not found.'})
    
    if 'logo' in request.FILES:
        employer.logo = request.FILES['logo']
        employer.save()
        return JsonResponse({
            'success': True,
            'logo_url': employer.logo.url if employer.logo else None,
            'message': 'Logo uploaded successfully!'
        })
    
    return JsonResponse({'success': False, 'error': 'No logo file provided.'})


@login_required
@require_POST
def upload_verification_documents(request):
    """Upload verification documents via AJAX"""
    if request.user.user_type != 'employer':
        return JsonResponse({'success': False, 'error': 'Access denied.'})
    
    try:
        employer = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Employer profile not found.'})
    
    document_type = request.POST.get('document_type')
    document_file = request.FILES.get('document')
    
    if document_type and document_file:
        doc = EmployerDocument.objects.create(
            employer=employer,
            document_type=document_type,
            document=document_file,
            description=request.POST.get('description', '')
        )
        return JsonResponse({
            'success': True,
            'document_id': str(doc.id),
            'document_type': doc.get_document_type_display(),
            'document_url': doc.document.url if doc.document else None,
            'message': 'Document uploaded successfully!'
        })
    
    return JsonResponse({'success': False, 'error': 'Please provide document type and file.'})


@login_required
@require_POST
def delete_verification_document(request, doc_id):
    """Delete a verification document"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied.')
        return redirect('employer_dashboard')
    
    doc = get_object_or_404(EmployerDocument, id=doc_id, employer__user=request.user)
    doc.delete()
    messages.success(request, 'Document deleted successfully.')
    return redirect('employer_verification')


@login_required
@require_GET
def employer_stats_ajax(request):
    """Get employer dashboard statistics via AJAX"""
    if request.user.user_type != 'employer':
        return JsonResponse({'error': 'Access denied.'}, status=403)
    
    try:
        employer = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        return JsonResponse({'error': 'Employer not found.'}, status=404)
    
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
    }
    return JsonResponse(stats)


# ==============================================
# EMPLOYER DASHBOARD VIEWS
# ==============================================

@login_required
def employer_dashboard(request):
    """Employer dashboard view"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied. This is for employers only.')
        return redirect('home')
    
    try:
        employer = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Please complete your employer profile first.')
        return redirect('employer_setup')
    
    # Get statistics
    jobs = Job.objects.filter(employer=employer)
    applications = JobApplication.objects.filter(job__employer=employer)
    
    context = {
        'employer': employer,
        'jobs_count': jobs.count(),
        'active_jobs': jobs.filter(status='active').count(),
        'total_applications': applications.count(),
        'shortlisted': applications.filter(status='shortlisted').count(),
        'total_views': jobs.aggregate(Sum('views_count'))['views_count__sum'] or 0,
        'new_applications_today': applications.filter(date_applied__date=timezone.now().date()).count(),
        'expiring_jobs': jobs.filter(
            closing_date__lte=timezone.now() + timedelta(days=7),
            status='active'
        ).count(),
        'expired_jobs': jobs.filter(
            closing_date__lt=timezone.now(),
            status='active'
        ).count(),
        'recent_jobs': jobs.order_by('-posted_date')[:5],
        'recent_applications': applications.select_related('applicant', 'job').order_by('-date_applied')[:5],
    }
    return render(request, 'employers/dashboard.html', context)


@login_required
def employer_job_list(request):
    """List all jobs for an employer"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    employer = get_object_or_404(EmployerProfile, user=request.user)
    jobs = Job.objects.filter(employer=employer).order_by('-posted_date')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        jobs = jobs.filter(status=status)
    
    # Filter by date
    date_filter = request.GET.get('date_filter')
    if date_filter == 'today':
        jobs = jobs.filter(posted_date__date=timezone.now().date())
    elif date_filter == 'week':
        jobs = jobs.filter(posted_date__gte=timezone.now() - timedelta(days=7))
    elif date_filter == 'month':
        jobs = jobs.filter(posted_date__gte=timezone.now() - timedelta(days=30))
    
    paginator = Paginator(jobs, 10)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    
    context = {
        'employer': employer,
        'jobs': jobs,
        'status_choices': Job.STATUS_CHOICES,
        'current_status': status,
        'date_filter': date_filter,
    }
    return render(request, 'employers/job_list.html', context)


@login_required
def create_job(request):
    """Create a new job posting"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied. This is for employers only.')
        return redirect('home')
    
    try:
        employer = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Please complete your employer profile first.')
        return redirect('employer_setup')
    
    if not employer.is_verified:
        messages.warning(request, 'Your account needs to be verified before you can post jobs.')
        return redirect('employer_verification')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = employer
            job.posted_date = timezone.now()
            
            # Set default status
            if employer.is_verified:
                job.status = 'active'
                job.is_verified = True
            else:
                job.status = 'pending'
                job.is_verified = False
            
            job.save()
            messages.success(request, f'Job "{job.title}" posted successfully!')
            return redirect('employer_job_list')
    else:
        form = JobForm()
    
    context = {
        'form': form,
        'employer': employer,
    }
    return render(request, 'employers/create_job.html', context)


@login_required
def edit_job(request, job_id):
    """Edit an existing job posting"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    employer = get_object_or_404(EmployerProfile, user=request.user)
    job = get_object_or_404(Job, id=job_id, employer=employer)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            job = form.save(commit=False)
            job.updated_at = timezone.now()
            job.save()
            messages.success(request, f'Job "{job.title}" updated successfully!')
            return redirect('employer_job_list')
    else:
        form = JobForm(instance=job)
    
    context = {
        'form': form,
        'job': job,
        'employer': employer,
    }
    return render(request, 'employers/edit_job.html', context)


@login_required
def job_applications(request, job_id):
    """View all applications for a specific job"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    employer = get_object_or_404(EmployerProfile, user=request.user)
    job = get_object_or_404(Job, id=job_id, employer=employer)
    applications = JobApplication.objects.filter(job=job).order_by('-date_applied')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        applications = applications.filter(status=status)
    
    paginator = Paginator(applications, 20)
    page = request.GET.get('page')
    applications = paginator.get_page(page)
    
    context = {
        'job': job,
        'employer': employer,
        'applications': applications,
        'status_choices': JobApplication.STATUS_CHOICES,
        'current_status': status,
        'total_applications': JobApplication.objects.filter(job=job).count(),
    }
    return render(request, 'employers/job_applications.html', context)


@login_required
def update_application_status(request, app_id):
    """Update the status of an application"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    application = get_object_or_404(
        JobApplication,
        id=app_id,
        job__employer__user=request.user
    )
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if new_status in dict(JobApplication.STATUS_CHOICES):
            application.status = new_status
            application.date_status_changed = timezone.now()
            
            if notes:
                application.review_notes = notes
            
            application.save()
            
            # Create notification for the applicant
            Notification.objects.create(
                user=application.applicant,
                title=f'Application Status Update: {application.job.title}',
                message=f'Your application for "{application.job.title}" has been updated to {application.get_status_display()}.',
                notification_type='application_update',
                related_object_id=str(application.id),
            )
            
            messages.success(request, f'Application status updated to {application.get_status_display()}')
        else:
            messages.error(request, 'Invalid status selected.')
        
        return redirect('job_applications', job_id=application.job.id)
    
    context = {
        'application': application,
        'status_choices': JobApplication.STATUS_CHOICES,
    }
    return render(request, 'employers/update_status.html', context)


@login_required
def view_application(request, app_id):
    """View a single application in detail"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    application = get_object_or_404(
        JobApplication,
        id=app_id,
        job__employer__user=request.user
    )
    
    context = {
        'application': application,
    }
    return render(request, 'employers/view_application.html', context)


@login_required
@require_POST
def bulk_application_action(request):
    """Bulk action on multiple applications"""
    if request.user.user_type != 'employer':
        return JsonResponse({'error': 'Access denied.'}, status=403)
    
    application_ids = request.POST.getlist('application_ids[]')
    action = request.POST.get('action')
    
    if not application_ids or not action:
        return JsonResponse({'error': 'No applications or action selected.'}, status=400)
    
    applications = JobApplication.objects.filter(
        id__in=application_ids,
        job__employer__user=request.user
    )
    
    if action == 'shortlist':
        applications.update(status='shortlisted')
    elif action == 'reject':
        applications.update(status='rejected')
    elif action == 'withdraw':
        applications.update(status='withdrawn')
    elif action == 'interview':
        applications.update(status='interview_scheduled')
    else:
        return JsonResponse({'error': 'Invalid action.'}, status=400)
    
    return JsonResponse({
        'success': True,
        'message': f'{applications.count()} applications updated successfully.'
    })


@login_required
@require_POST
def delete_job(request, job_id):
    """Delete a job posting (soft delete)"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    job = get_object_or_404(Job, id=job_id, employer__user=request.user)
    job.status = 'closed'
    job.save()
    
    messages.success(request, f'Job "{job.title}" has been closed.')
    return redirect('employer_job_list')


@login_required
@require_GET
def employer_recent_activity(request):
    """Get recent employer activity via AJAX"""
    if request.user.user_type != 'employer':
        return JsonResponse({'error': 'Access denied.'}, status=403)
    
    employer = get_object_or_404(EmployerProfile, user=request.user)
    
    # Get recent activity (jobs and applications)
    recent_jobs = Job.objects.filter(employer=employer).order_by('-posted_date')[:3]
    recent_applications = JobApplication.objects.filter(
        job__employer=employer
    ).order_by('-date_applied')[:3]
    
    activity = []
    
    for job in recent_jobs:
        activity.append({
            'type': 'job',
            'title': job.title,
            'date': job.posted_date.strftime('%Y-%m-%d %H:%M'),
            'status': job.status,
            'url': f'/employer/jobs/{job.id}/edit/'
        })
    
    for app in recent_applications:
        activity.append({
            'type': 'application',
            'title': f'{app.applicant.full_name} applied to {app.job.title}',
            'date': app.date_applied.strftime('%Y-%m-%d %H:%M'),
            'status': app.status,
            'url': f'/employer/applications/{app.id}/view/'
        })
    
    # Sort by date
    activity.sort(key=lambda x: x['date'], reverse=True)
    
    return JsonResponse({'activity': activity[:5]})


# ==============================================
# ADMIN EMPLOYER MANAGEMENT (for admin panel)
# ==============================================

@login_required
def admin_register_employer(request):
    """Admin register employer"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')
    
    if request.method == 'POST':
        form = EmployerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'employer'
            user.status = 'approved'
            user.is_verified = True
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            EmployerProfile.objects.create(
                user=user,
                company_name=form.cleaned_data.get('company_name', ''),
                contact_email=user.email,
                contact_phone=user.phone_number,
                is_verified=True,
                verification_date=timezone.now()
            )
            
            messages.success(request, f'Employer {user.full_name} registered successfully!')
            return redirect('admin_panel:admin_employer_list')
    else:
        form = EmployerRegistrationForm()
    
    context = {'form': form}
    return render(request, 'admin_panel/employers/register.html', context)


@login_required
def admin_employer_setup(request, employer_id):
    """Admin complete employer setup"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')
    
    employer = get_object_or_404(EmployerProfile, id=employer_id)
    
    if request.method == 'POST':
        form = EmployerProfileForm(request.POST, request.FILES, instance=employer)
        if form.is_valid():
            form.save()
            messages.success(request, f'Employer {employer.company_name} profile updated!')
            return redirect('admin_panel:admin_employer_detail', employer_id=employer_id)
    else:
        form = EmployerProfileForm(instance=employer)
    
    context = {
        'form': form,
        'employer': employer,
    }
    return render(request, 'admin_panel/employers/setup.html', context)


@login_required
def admin_employer_stats(request, employer_id):
    """Get employer statistics for admin (AJAX)"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied.'}, status=403)
    
    employer = get_object_or_404(EmployerProfile, id=employer_id)
    
    jobs = Job.objects.filter(employer=employer)
    applications = JobApplication.objects.filter(job__employer=employer)
    
    stats = {
        'company_name': employer.company_name,
        'is_verified': employer.is_verified,
        'verification_date': employer.verification_date.strftime('%Y-%m-%d') if employer.verification_date else None,
        'total_jobs': jobs.count(),
        'active_jobs': jobs.filter(status='active').count(),
        'pending_jobs': jobs.filter(status='pending').count(),
        'rejected_jobs': jobs.filter(status='rejected').count(),
        'total_applications': applications.count(),
        'shortlisted': applications.filter(status='shortlisted').count(),
        'accepted': applications.filter(status='accepted').count(),
        'rejected': applications.filter(status='rejected').count(),
    }
    return JsonResponse(stats)


def employer_jobs_api(request, employer_id):
    """API endpoint for employer jobs"""
    employer = get_object_or_404(EmployerProfile, id=employer_id, is_verified=True)
    
    jobs = Job.objects.filter(
        employer=employer,
        status='active',
        is_verified=True,
        closing_date__gte=timezone.now()
    ).select_related('country', 'category')
    
    data = []
    for job in jobs:
        data.append({
            'id': str(job.id),
            'title': job.title,
            'country': job.country.name,
            'category': job.category.name,
            'salary': f"{job.salary_currency} {job.salary_min}" if job.salary_min else None,
            'employment_type': job.get_employment_type_display(),
            'closing_date': job.closing_date.strftime('%Y-%m-%d'),
            'url': f'/jobs/{job.id}/'
        })
    
    return JsonResponse({'jobs': data})