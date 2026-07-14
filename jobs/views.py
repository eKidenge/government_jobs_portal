"""
Jobs Views
Handles job listings, details, applications, and management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings

from .models import Job, Category, Country, JobApplication
from .forms import JobSearchForm, JobApplicationForm
from accounts.models import User
from employers.models import EmployerProfile
from agencies.models import RecruitmentAgency
from payments.models import UserPaymentAccess
from notifications.models import Notification


def job_list(request):
    """List all jobs with filtering"""
    jobs = Job.objects.filter(
        status='active',
        is_verified=True,
        closing_date__gte=timezone.now()
    ).select_related('country', 'category', 'employer', 'agency')
    
    # Search and filter
    form = JobSearchForm(request.GET)
    if form.is_valid():
        search = form.cleaned_data.get('search')
        country = form.cleaned_data.get('country')
        category = form.cleaned_data.get('category')
        employment_type = form.cleaned_data.get('employment_type')
        experience_level = form.cleaned_data.get('experience_level')
        salary_min = form.cleaned_data.get('salary_min')
        salary_max = form.cleaned_data.get('salary_max')
        
        if search:
            jobs = jobs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(requirements__icontains=search) |
                Q(employer__company_name__icontains=search) |
                Q(agency__agency_name__icontains=search)
            )
        if country:
            jobs = jobs.filter(country_id=country)
        if category:
            jobs = jobs.filter(category_id=category)
        if employment_type:
            jobs = jobs.filter(employment_type=employment_type)
        if experience_level:
            jobs = jobs.filter(experience_level=experience_level)
        if salary_min:
            jobs = jobs.filter(salary_min__gte=salary_min)
        if salary_max:
            jobs = jobs.filter(salary_max__lte=salary_max)
    
    # Sort
    sort = request.GET.get('sort', '-posted_date')
    jobs = jobs.order_by(sort)
    
    # Pagination
    paginator = Paginator(jobs, 12)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    
    # Get filter options
    countries = Country.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    employment_types = Job.EMPLOYMENT_TYPES
    experience_levels = Job.EXPERIENCE_LEVELS
    
    context = {
        'jobs': jobs,
        'paginator': paginator,
        'countries': countries,
        'categories': categories,
        'employment_types': employment_types,
        'experience_levels': experience_levels,
        'current_filters': request.GET,
    }
    return render(request, 'jobs/job_list.html', context)


def job_detail(request, job_id):
    """View job details"""
    job = get_object_or_404(
        Job.objects.select_related('country', 'category', 'employer', 'agency'),
        id=job_id,
        status='active',
        is_verified=True
    )
    
    # Increment view count
    job.views_count += 1
    job.save(update_fields=['views_count'])
    
    # Check if user has payment access (if logged in)
    has_payment_access = False
    if request.user.is_authenticated:
        try:
            payment_access = UserPaymentAccess.objects.get(user=request.user)
            has_payment_access = payment_access.can_apply()
        except UserPaymentAccess.DoesNotExist:
            has_payment_access = False
    
    # Get similar jobs
    similar_jobs = Job.objects.filter(
        Q(category=job.category) | Q(country=job.country),
        status='active',
        is_verified=True,
        closing_date__gte=timezone.now()
    ).exclude(id=job.id)[:5]
    
    context = {
        'job': job,
        'has_payment_access': has_payment_access,
        'similar_jobs': similar_jobs,
        'now': timezone.now(),
    }
    return render(request, 'jobs/job_detail.html', context)


@login_required
def apply_to_job(request, job_id):
    """Apply to a job"""
    job = get_object_or_404(
        Job,
        id=job_id,
        status='active',
        is_verified=True,
        closing_date__gte=timezone.now()
    )
    
    # Check if user is a citizen
    if request.user.user_type != 'citizen':
        messages.error(request, 'Only citizens can apply for jobs.')
        return redirect('job_detail', job_id=job_id)
    
    # Check if user has payment access
    try:
        payment_access = UserPaymentAccess.objects.get(user=request.user)
        if not payment_access.can_apply():
            messages.error(request, 'Please complete the government employment service fee payment before applying.')
            return redirect('payment_page')
    except UserPaymentAccess.DoesNotExist:
        messages.error(request, 'Please complete the government employment service fee payment before applying.')
        return redirect('payment_page')
    
    # Check if already applied
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this position.')
        return redirect('job_detail', job_id=job_id)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            
            # Update job application count
            job.applications_count += 1
            job.save(update_fields=['applications_count'])
            
            # Update payment access usage
            payment_access.applications_used += 1
            payment_access.save(update_fields=['applications_used'])
            
            # Create notification for applicant
            Notification.objects.create(
                user=request.user,
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
                    message=f'{request.user.full_name} has applied for "{job.title}".',
                    notification_type='application_received',
                    link=f'/employer/applications/{application.id}/'
                )
            elif job.agency:
                Notification.objects.create(
                    user=job.agency.user,
                    title='New Application Received',
                    message=f'{request.user.full_name} has applied for "{job.title}".',
                    notification_type='application_received',
                    link=f'/agency/applications/{application.id}/'
                )
            
            # Send confirmation email
            try:
                subject = f'Application Submitted - {job.title}'
                html_message = render_to_string('emails/application_confirmation.html', {
                    'user': request.user,
                    'job': job,
                    'application': application,
                    'site_url': settings.SITE_URL
                })
                plain_message = strip_tags(html_message)
                send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [request.user.email], html_message=html_message)
            except Exception as e:
                print(f"Email sending failed: {e}")
            
            messages.success(request, f'Your application for "{job.title}" has been submitted successfully!')
            return redirect('my_applications')
    else:
        form = JobApplicationForm()
    
    context = {
        'job': job,
        'form': form,
    }
    return render(request, 'jobs/apply_to_job.html', context)


@login_required
def my_applications(request):
    """View user's job applications"""
    applications = JobApplication.objects.filter(
        applicant=request.user
    ).select_related('job', 'job__employer', 'job__country').order_by('-date_applied')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    paginator = Paginator(applications, 10)
    page = request.GET.get('page')
    applications = paginator.get_page(page)
    
    context = {
        'applications': applications,
        'status_filter': status_filter,
        'status_choices': JobApplication.STATUS_CHOICES,
    }
    return render(request, 'jobs/my_applications.html', context)


@login_required
def application_detail(request, app_id):
    """View application details"""
    application = get_object_or_404(
        JobApplication.objects.select_related('job', 'job__employer', 'job__country', 'applicant'),
        id=app_id,
        applicant=request.user
    )
    
    context = {
        'application': application,
    }
    return render(request, 'jobs/application_detail.html', context)


@login_required
@require_POST
def withdraw_application(request, app_id):
    """Withdraw an application"""
    application = get_object_or_404(
        JobApplication,
        id=app_id,
        applicant=request.user,
        status__in=['submitted', 'under_review']
    )
    
    application.status = 'withdrawn'
    application.save()
    
    messages.success(request, 'Application withdrawn successfully.')
    return redirect('my_applications')


@login_required
def country_list(request):
    """List all countries with job counts"""
    countries = Country.objects.filter(
        is_active=True,
        jobs__status='active',
        jobs__is_verified=True,
        jobs__closing_date__gte=timezone.now()
    ).annotate(
        job_count=Count('jobs')
    ).filter(job_count__gt=0).order_by('name')
    
    context = {'countries': countries}
    return render(request, 'jobs/country_list.html', context)


@login_required
def country_jobs(request, country_slug):
    """List jobs in a specific country"""
    country = get_object_or_404(Country, slug=country_slug, is_active=True)
    jobs = Job.objects.filter(
        country=country,
        status='active',
        is_verified=True,
        closing_date__gte=timezone.now()
    ).select_related('category', 'employer', 'agency')
    
    paginator = Paginator(jobs, 12)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    
    context = {
        'country': country,
        'jobs': jobs,
        'paginator': paginator,
    }
    return render(request, 'jobs/country_jobs.html', context)


@login_required
def category_list(request):
    """List all categories with job counts"""
    categories = Category.objects.filter(
        is_active=True,
        jobs__status='active',
        jobs__is_verified=True,
        jobs__closing_date__gte=timezone.now()
    ).annotate(
        job_count=Count('jobs')
    ).filter(job_count__gt=0).order_by('name')
    
    context = {'categories': categories}
    return render(request, 'jobs/category_list.html', context)


@login_required
def category_jobs(request, category_slug):
    """List jobs in a specific category"""
    category = get_object_or_404(Category, slug=category_slug, is_active=True)
    jobs = Job.objects.filter(
        category=category,
        status='active',
        is_verified=True,
        closing_date__gte=timezone.now()
    ).select_related('country', 'employer', 'agency')
    
    paginator = Paginator(jobs, 12)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    
    context = {
        'category': category,
        'jobs': jobs,
        'paginator': paginator,
    }
    return render(request, 'jobs/category_jobs.html', context)


# ==============================================
# EMPLOYER JOB MANAGEMENT
# ==============================================

@login_required
def employer_job_list(request):
    """List jobs posted by the employer"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied. This is for employers only.')
        return redirect('home')
    
    try:
        employer = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Please complete your employer profile first.')
        return redirect('employer_setup')
    
    jobs = Job.objects.filter(employer=employer).order_by('-posted_date')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        jobs = jobs.filter(status=status_filter)
    
    paginator = Paginator(jobs, 20)
    page = request.GET.get('page')
    jobs = paginator.get_page(page)
    
    context = {
        'jobs': jobs,
        'status_filter': status_filter,
        'status_choices': Job.STATUS_CHOICES,
    }
    return render(request, 'jobs/employer_job_list.html', context)


@login_required
def create_job(request):
    """Create a new job posting"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied. This is for employers only.')
        return redirect('home')
    
    try:
        employer = EmployerProfile.objects.get(user=request.user)
        if not employer.is_verified:
            messages.error(request, 'Your employer account must be verified before posting jobs.')
            return redirect('employer_dashboard')
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Please complete your employer profile first.')
        return redirect('employer_setup')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = employer
            job.status = 'pending'
            job.posted_by = request.user
            job.save()
            
            messages.success(request, 'Job posted successfully! It will be reviewed by the admin.')
            return redirect('employer_job_list')
    else:
        form = JobForm()
    
    context = {'form': form}
    return render(request, 'jobs/create_job.html', context)


@login_required
def edit_job(request, job_id):
    """Edit a job posting"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied. This is for employers only.')
        return redirect('home')
    
    try:
        employer = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Please complete your employer profile first.')
        return redirect('employer_setup')
    
    job = get_object_or_404(Job, id=job_id, employer=employer)
    
    if job.status in ['approved', 'active']:
        messages.warning(request, 'This job is already live. Only pending jobs can be edited.')
        return redirect('employer_job_list')
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('employer_job_list')
    else:
        form = JobForm(instance=job)
    
    context = {'form': form, 'job': job}
    return render(request, 'jobs/edit_job.html', context)


@login_required
@require_POST
def delete_job(request, job_id):
    """Delete a job posting"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied. This is for employers only.')
        return redirect('home')
    
    try:
        employer = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Please complete your employer profile first.')
        return redirect('employer_setup')
    
    job = get_object_or_404(Job, id=job_id, employer=employer)
    job_title = job.title
    job.delete()
    
    messages.success(request, f'Job "{job_title}" deleted successfully.')
    return redirect('employer_job_list')


@login_required
@require_POST
def toggle_job_status(request, job_id):
    """Toggle job status (close/reopen)"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied. This is for employers only.')
        return redirect('home')
    
    try:
        employer = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Please complete your employer profile first.')
        return redirect('employer_setup')
    
    job = get_object_or_404(Job, id=job_id, employer=employer)
    
    if job.status == 'active':
        job.status = 'closed'
        messages.success(request, f'Job "{job.title}" closed.')
    elif job.status == 'closed':
        job.status = 'active'
        messages.success(request, f'Job "{job.title}" reopened.')
    else:
        messages.warning(request, 'Only active or closed jobs can be toggled.')
        return redirect('employer_job_list')
    
    job.save()
    return redirect('employer_job_list')


@login_required
def job_applications(request, job_id):
    """View applications for a specific job"""
    if request.user.user_type not in ['employer', 'agency']:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    if request.user.user_type == 'employer':
        try:
            employer = EmployerProfile.objects.get(user=request.user)
        except EmployerProfile.DoesNotExist:
            messages.error(request, 'Please complete your profile first.')
            return redirect('employer_setup')
        job = get_object_or_404(Job, id=job_id, employer=employer)
    else:
        try:
            agency = RecruitmentAgency.objects.get(user=request.user)
        except RecruitmentAgency.DoesNotExist:
            messages.error(request, 'Please complete your profile first.')
            return redirect('agency_setup')
        job = get_object_or_404(Job, id=job_id, agency=agency)
    
    applications = JobApplication.objects.filter(job=job).select_related('applicant').order_by('-date_applied')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    paginator = Paginator(applications, 20)
    page = request.GET.get('page')
    applications = paginator.get_page(page)
    
    context = {
        'job': job,
        'applications': applications,
        'status_filter': status_filter,
        'status_choices': JobApplication.STATUS_CHOICES,
    }
    return render(request, 'jobs/job_applications.html', context)


@login_required
@require_POST
def update_application_status(request, app_id):
    """Update application status"""
    if request.user.user_type not in ['employer', 'agency']:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    application = get_object_or_404(
        JobApplication.objects.select_related('job', 'applicant'),
        id=app_id
    )
    
    # Check permission
    if request.user.user_type == 'employer':
        if application.job.employer.user != request.user:
            messages.error(request, 'Access denied.')
            return redirect('home')
    elif request.user.user_type == 'agency':
        if application.job.agency.user != request.user:
            messages.error(request, 'Access denied.')
            return redirect('home')
    
    new_status = request.POST.get('status')
    notes = request.POST.get('notes', '')
    
    if new_status in dict(JobApplication.STATUS_CHOICES):
        application.status = new_status
        if notes:
            application.review_notes = notes
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
        
        messages.success(request, f'Application status updated to {application.get_status_display()}.')
    else:
        messages.error(request, 'Invalid status.')
    
    return redirect('job_applications', job_id=application.job.id)


@login_required
def add_application_notes(request, app_id):
    """Add notes to an application"""
    if request.user.user_type not in ['employer', 'agency']:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    application = get_object_or_404(
        JobApplication.objects.select_related('job', 'applicant'),
        id=app_id
    )
    
    # Check permission
    if request.user.user_type == 'employer':
        if application.job.employer.user != request.user:
            messages.error(request, 'Access denied.')
            return redirect('home')
    elif request.user.user_type == 'agency':
        if application.job.agency.user != request.user:
            messages.error(request, 'Access denied.')
            return redirect('home')
    
    if request.method == 'POST':
        notes = request.POST.get('notes', '')
        if notes:
            application.review_notes = notes
            application.save()
            messages.success(request, 'Notes added successfully.')
        else:
            messages.warning(request, 'Please enter some notes.')
    
    return redirect('job_applications', job_id=application.job.id)


@login_required
def download_cv(request, app_id):
    """Download applicant's CV"""
    if request.user.user_type not in ['employer', 'agency']:
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    application = get_object_or_404(
        JobApplication.objects.select_related('job', 'applicant', 'applicant__profile'),
        id=app_id
    )
    
    # Check permission
    if request.user.user_type == 'employer':
        if application.job.employer.user != request.user:
            messages.error(request, 'Access denied.')
            return redirect('home')
    elif request.user.user_type == 'agency':
        if application.job.agency.user != request.user:
            messages.error(request, 'Access denied.')
            return redirect('home')
    
    try:
        cv = application.applicant.profile.cv
        if cv:
            response = HttpResponse(cv.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{application.applicant.full_name}_CV.pdf"'
            return response
        else:
            messages.error(request, 'No CV uploaded by this applicant.')
    except Exception as e:
        messages.error(request, f'Error downloading CV: {str(e)}')
    
    return redirect('job_applications', job_id=application.job.id)


# ==============================================
# AJAX ENDPOINTS
# ==============================================

@require_GET
def featured_jobs_ajax(request):
    """Get featured jobs for AJAX"""
    jobs = Job.objects.filter(
        status='active',
        is_featured=True,
        is_verified=True,
        closing_date__gte=timezone.now()
    ).select_related('country', 'category', 'employer', 'agency').order_by('-posted_date')[:10]
    
    data = []
    for job in jobs:
        data.append({
            'id': str(job.id),
            'title': job.title,
            'employer': job.employer.company_name if job.employer else job.agency.agency_name if job.agency else 'N/A',
            'country': job.country.name,
            'salary': f"{job.salary_currency} {job.salary_min}" if job.salary_min else 'N/A',
            'employment_type': job.get_employment_type_display(),
            'closing_date': job.closing_date.strftime('%b %d, %Y'),
            'url': f'/jobs/{job.id}/'
        })
    
    return JsonResponse({'jobs': data})


@require_GET
def job_statistics_ajax(request):
    """Get job statistics for AJAX"""
    stats = {
        'available_jobs': Job.objects.filter(status='active', closing_date__gte=timezone.now()).count(),
        'registered_job_seekers': User.objects.filter(user_type='citizen', status='approved').count(),
        'verified_employers': EmployerProfile.objects.filter(is_verified=True).count(),
        'countries_recruiting': Job.objects.filter(status='active').values('country').distinct().count(),
        'successful_placements': JobApplication.objects.filter(status='accepted').count(),
        'licensed_recruitment_agencies': RecruitmentAgency.objects.filter(is_verified=True).count(),
    }
    return JsonResponse(stats)


def job_list_api(request):
    """API endpoint for job list"""
    jobs = Job.objects.filter(
        status='active',
        is_verified=True,
        closing_date__gte=timezone.now()
    ).select_related('country', 'category', 'employer', 'agency')
    
    # Apply filters
    country = request.GET.get('country')
    category = request.GET.get('category')
    search = request.GET.get('search')
    
    if country:
        jobs = jobs.filter(country_id=country)
    if category:
        jobs = jobs.filter(category_id=category)
    if search:
        jobs = jobs.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
    
    jobs = jobs.order_by('-posted_date')[:50]
    
    data = []
    for job in jobs:
        data.append({
            'id': str(job.id),
            'title': job.title,
            'employer': job.employer.company_name if job.employer else job.agency.agency_name if job.agency else 'N/A',
            'country': job.country.name,
            'category': job.category.name,
            'salary': f"{job.salary_currency} {job.salary_min}" if job.salary_min else None,
            'employment_type': job.get_employment_type_display(),
            'closing_date': job.closing_date.strftime('%Y-%m-%d'),
            'url': f'/jobs/{job.id}/'
        })
    
    return JsonResponse({'jobs': data})