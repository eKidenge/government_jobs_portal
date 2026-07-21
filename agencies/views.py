"""
Agencies Views (Recruitment Agencies)
Handles agency registration, profile management, and dashboard
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET
from datetime import timedelta  # ADDED: Import for timedelta

from .models import RecruitmentAgency, AgencyDocument, AgencyApplication, AgencyContract, AgencyRecruitmentProcess
from .forms import AgencyProfileForm
from accounts.models import User
from accounts.forms import AgencyRegistrationForm
from jobs.models import Job, JobApplication, Country
from jobs.forms import JobForm
from notifications.models import Notification


def agency_list(request):
    """List all verified recruitment agencies"""
    agencies = RecruitmentAgency.objects.filter(
        is_verified=True
    ).select_related('user', 'country').order_by('agency_name')
    
    # Search
    search = request.GET.get('search')
    if search:
        agencies = agencies.filter(
            Q(agency_name__icontains=search) |
            Q(description__icontains=search) |
            Q(specializations__icontains=search)
        )
    
    # Filter by country
    country = request.GET.get('country')
    if country:
        agencies = agencies.filter(country_id=country)
    
    # Annotate with job count
    agencies = agencies.annotate(
        job_count=Count('jobs', filter=Q(jobs__status='active', jobs__closing_date__gte=timezone.now()))
    )
    
    paginator = Paginator(agencies, 12)
    page = request.GET.get('page')
    agencies = paginator.get_page(page)
    
    # Get filter options
    countries = Country.objects.filter(is_active=True)
    
    context = {
        'agencies': agencies,
        'paginator': paginator,
        'countries': countries,
        'current_filters': request.GET,
    }
    return render(request, 'agencies/list.html', context)


def agency_detail(request, agency_id):
    """View agency details"""
    agency = get_object_or_404(
        RecruitmentAgency.objects.select_related('user', 'country'),
        id=agency_id,
        is_verified=True
    )
    
    # Get active jobs
    jobs = Job.objects.filter(
        agency=agency,
        status='active',
        is_verified=True,
        closing_date__gte=timezone.now()
    ).select_related('country', 'category').order_by('-posted_date')
    
    # Get job count
    job_count = jobs.count()
    
    # Get recent jobs (limit to 5)
    recent_jobs = jobs[:5]
    
    # Get active countries
    active_countries = agency.active_countries.all()
    
    context = {
        'agency': agency,
        'jobs': jobs,
        'recent_jobs': recent_jobs,
        'job_count': job_count,
        'active_countries': active_countries,
        'total_applications': JobApplication.objects.filter(job__agency=agency).count(),
        'now': timezone.now().date(),
    }
    return render(request, 'agencies/detail.html', context)


def agency_register(request):
    """Agency registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AgencyRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'agency'
            user.status = 'pending'
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Create agency profile (will be completed in setup)
            RecruitmentAgency.objects.create(
                user=user,
                agency_name=form.cleaned_data.get('agency_name', ''),
                contact_email=user.email,
                contact_phone=user.phone_number,
                # Set default license expiry to 1 year from now
                license_expiry=timezone.now().date() + timedelta(days=365)
            )
            
            messages.success(request, 'Agency account created! Please complete your profile setup.')
            return redirect('agencies:agency_setup')
    else:
        form = AgencyRegistrationForm()
    
    context = {'form': form}
    return render(request, 'agencies/register.html', context)


@login_required
def agency_setup(request):
    """Complete agency profile setup"""
    if request.user.user_type != 'agency':
        messages.error(request, 'Access denied. This is for recruitment agencies only.')
        return redirect('home')
    
    try:
        agency = RecruitmentAgency.objects.get(user=request.user)
    except RecruitmentAgency.DoesNotExist:
        # FIXED: Create with default license_expiry to avoid NOT NULL constraint error
        agency = RecruitmentAgency.objects.create(
            user=request.user,
            license_expiry=timezone.now().date() + timedelta(days=365)  # Default: 1 year from now
        )
    
    if request.method == 'POST':
        form = AgencyProfileForm(request.POST, request.FILES, instance=agency)
        if form.is_valid():
            agency = form.save(commit=False)
            agency.user = request.user
            
            # Handle logo upload
            if 'logo' in request.FILES:
                agency.logo = request.FILES['logo']
            
            agency.save()
            
            # Save many-to-many relationships
            if 'active_countries' in request.POST:
                country_ids = request.POST.getlist('active_countries')
                agency.active_countries.set(country_ids)
            
            messages.success(request, 'Agency profile completed successfully!')
            return redirect('agencies:agency_dashboard')
    else:
        form = AgencyProfileForm(instance=agency)
    
    countries = Country.objects.filter(is_active=True)
    
    context = {
        'form': form,
        'agency': agency,
        'countries': countries,
    }
    return render(request, 'agencies/setup.html', context)


@login_required
def agency_verification(request):
    """Upload accreditation documents"""
    if request.user.user_type != 'agency':
        messages.error(request, 'Access denied. This is for recruitment agencies only.')
        return redirect('home')
    
    try:
        agency = RecruitmentAgency.objects.get(user=request.user)
    except RecruitmentAgency.DoesNotExist:
        messages.error(request, 'Please complete your agency profile first.')
        return redirect('agencies:agency_setup')
    
    if request.method == 'POST':
        document_type = request.POST.get('document_type')
        document_file = request.FILES.get('document')
        
        if document_type and document_file:
            AgencyDocument.objects.create(
                agency=agency,
                document_type=document_type,
                document=document_file,
                description=request.POST.get('description', '')
            )
            messages.success(request, 'Document uploaded successfully!')
        else:
            messages.error(request, 'Please select a document type and file.')
        
        return redirect('agencies:agency_verification')
    
    documents = AgencyDocument.objects.filter(agency=agency)
    
    context = {
        'agency': agency,
        'documents': documents,
        'document_types': AgencyDocument.DOCUMENT_TYPES,
    }
    return render(request, 'agencies/verification.html', context)


@login_required
def agency_profile_update(request):
    """Update agency profile"""
    if request.user.user_type != 'agency':
        messages.error(request, 'Access denied. This is for recruitment agencies only.')
        return redirect('home')
    
    try:
        agency = RecruitmentAgency.objects.get(user=request.user)
    except RecruitmentAgency.DoesNotExist:
        messages.error(request, 'Please complete your agency profile first.')
        return redirect('agencies:agency_setup')
    
    if request.method == 'POST':
        form = AgencyProfileForm(request.POST, request.FILES, instance=agency)
        if form.is_valid():
            agency = form.save()
            
            # Save many-to-many relationships
            if 'active_countries' in request.POST:
                country_ids = request.POST.getlist('active_countries')
                agency.active_countries.set(country_ids)
            
            # Update user info
            user = request.user
            if request.POST.get('full_name'):
                user.full_name = request.POST.get('full_name')
            if request.POST.get('phone_number'):
                user.phone_number = request.POST.get('phone_number')
            user.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('agencies:agency_dashboard')
    else:
        form = AgencyProfileForm(instance=agency)
    
    countries = Country.objects.filter(is_active=True)
    
    context = {
        'form': form,
        'agency': agency,
        'user': request.user,
        'countries': countries,
    }
    return render(request, 'agencies/profile_update.html', context)


@login_required
@require_POST
def agency_logo_upload(request):
    """Upload agency logo via AJAX"""
    if request.user.user_type != 'agency':
        return JsonResponse({'success': False, 'error': 'Access denied.'})
    
    try:
        agency = RecruitmentAgency.objects.get(user=request.user)
    except RecruitmentAgency.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agency profile not found.'})
    
    if 'logo' in request.FILES:
        agency.logo = request.FILES['logo']
        agency.save()
        return JsonResponse({
            'success': True,
            'logo_url': agency.logo.url if agency.logo else None,
            'message': 'Logo uploaded successfully!'
        })
    
    return JsonResponse({'success': False, 'error': 'No logo file provided.'})


@login_required
@require_POST
def upload_accreditation_documents(request):
    """Upload accreditation documents via AJAX"""
    if request.user.user_type != 'agency':
        return JsonResponse({'success': False, 'error': 'Access denied.'})
    
    try:
        agency = RecruitmentAgency.objects.get(user=request.user)
    except RecruitmentAgency.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Agency profile not found.'})
    
    document_type = request.POST.get('document_type')
    document_file = request.FILES.get('document')
    
    if document_type and document_file:
        doc = AgencyDocument.objects.create(
            agency=agency,
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
def delete_accreditation_document(request, doc_id):
    """Delete an accreditation document"""
    if request.user.user_type != 'agency':
        messages.error(request, 'Access denied.')
        return redirect('agencies:agency_dashboard')
    
    doc = get_object_or_404(AgencyDocument, id=doc_id, agency__user=request.user)
    doc.delete()
    messages.success(request, 'Document deleted successfully.')
    return redirect('agencies:agency_verification')


@login_required
def agency_job_list(request):
    """List jobs posted by the agency"""
    if request.user.user_type != 'agency':
        messages.error(request, 'Access denied. This is for recruitment agencies only.')
        return redirect('home')
    
    try:
        agency = RecruitmentAgency.objects.get(user=request.user)
    except RecruitmentAgency.DoesNotExist:
        messages.error(request, 'Please complete your agency profile first.')
        return redirect('agencies:agency_setup')
    
    jobs = Job.objects.filter(agency=agency).order_by('-posted_date')
    
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
    return render(request, 'agencies/job_list.html', context)


@login_required
def agency_create_job(request):
    """Create a new job posting (overseas opportunity)"""
    if request.user.user_type != 'agency':
        messages.error(request, 'Access denied. This is for recruitment agencies only.')
        return redirect('home')
    
    try:
        agency = RecruitmentAgency.objects.get(user=request.user)
        if not agency.is_verified:
            messages.error(request, 'Your agency must be verified before posting jobs.')
            return redirect('agencies:agency_dashboard')
    except RecruitmentAgency.DoesNotExist:
        messages.error(request, 'Please complete your agency profile first.')
        return redirect('agencies:agency_setup')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.agency = agency
            job.status = 'pending'
            job.posted_by = request.user
            job.save()
            
            messages.success(request, 'Job posted successfully! It will be reviewed by the admin.')
            return redirect('agencies:agency_job_list')
    else:
        form = JobForm()
        # Pre-populate country choices from agency's active countries
        form.fields['country'].choices = [(c.id, c.name) for c in agency.active_countries.all()]
    
    context = {'form': form}
    return render(request, 'agencies/create_job.html', context)


@login_required
def agency_edit_job(request, job_id):
    """Edit a job posting"""
    if request.user.user_type != 'agency':
        messages.error(request, 'Access denied. This is for recruitment agencies only.')
        return redirect('home')
    
    try:
        agency = RecruitmentAgency.objects.get(user=request.user)
    except RecruitmentAgency.DoesNotExist:
        messages.error(request, 'Please complete your agency profile first.')
        return redirect('agencies:agency_setup')
    
    job = get_object_or_404(Job, id=job_id, agency=agency)
    
    if job.status in ['approved', 'active']:
        messages.warning(request, 'This job is already live. Only pending jobs can be edited.')
        return redirect('agencies:agency_job_list')
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('agencies:agency_job_list')
    else:
        form = JobForm(instance=job)
        form.fields['country'].choices = [(c.id, c.name) for c in agency.active_countries.all()]
    
    context = {'form': form, 'job': job}
    return render(request, 'agencies/edit_job.html', context)


@login_required
@require_POST
def agency_delete_job(request, job_id):
    """Delete a job posting"""
    if request.user.user_type != 'agency':
        messages.error(request, 'Access denied. This is for recruitment agencies only.')
        return redirect('home')
    
    try:
        agency = RecruitmentAgency.objects.get(user=request.user)
    except RecruitmentAgency.DoesNotExist:
        messages.error(request, 'Please complete your agency profile first.')
        return redirect('agencies:agency_setup')
    
    job = get_object_or_404(Job, id=job_id, agency=agency)
    job_title = job.title
    
    # Check if job can be deleted
    if job.status in ['active', 'approved']:
        # Instead of deleting, just deactivate
        job.status = 'closed'
        job.save()
        messages.success(request, f'Job "{job_title}" has been closed.')
    else:
        job.delete()
        messages.success(request, f'Job "{job_title}" deleted successfully.')
    
    return redirect('agencies:agency_job_list')


@login_required
def agency_dashboard(request):
    """Agency dashboard view"""
    if request.user.user_type != 'agency':
        messages.error(request, 'Access denied. This is for recruitment agencies only.')
        return redirect('home')
    
    try:
        agency = RecruitmentAgency.objects.get(user=request.user)
    except RecruitmentAgency.DoesNotExist:
        messages.error(request, 'Please complete your agency profile first.')
        return redirect('agencies:agency_setup')
    
    # Get statistics
    jobs = Job.objects.filter(agency=agency)
    active_jobs = jobs.filter(status='active').count()
    pending_jobs = jobs.filter(status='pending').count()
    total_jobs = jobs.count()
    
    applications = JobApplication.objects.filter(job__agency=agency)
    total_applications = applications.count()
    
    # Recent jobs
    recent_jobs = jobs.order_by('-created_at')[:5]
    
    # Documents count
    documents_count = AgencyDocument.objects.filter(agency=agency).count()
    
    context = {
        'agency': agency,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'pending_jobs': pending_jobs,
        'total_applications': total_applications,
        'recent_jobs': recent_jobs,
        'documents_count': documents_count,
        'is_verified': agency.is_verified,
        'license_valid': agency.is_license_valid() if hasattr(agency, 'is_license_valid') else False,
        'license_expiry': agency.license_expiry,
        'now': timezone.now().date(),
    }
    return render(request, 'agencies/dashboard.html', context)


@login_required
@require_GET
def agency_stats_ajax(request):
    """Get agency dashboard statistics via AJAX"""
    if request.user.user_type != 'agency':
        return JsonResponse({'error': 'Access denied.'}, status=403)
    
    try:
        agency = RecruitmentAgency.objects.get(user=request.user)
    except RecruitmentAgency.DoesNotExist:
        return JsonResponse({'error': 'Agency not found.'}, status=404)
    
    jobs = Job.objects.filter(agency=agency)
    applications = JobApplication.objects.filter(job__agency=agency)
    agency_applications = AgencyApplication.objects.filter(agency=agency)
    
    stats = {
        'total_jobs': jobs.count(),
        'active_jobs': jobs.filter(status='active').count(),
        'pending_jobs': jobs.filter(status='pending').count(),
        'total_applications': applications.count(),
        'agency_applications': agency_applications.count(),
        'placements': agency_applications.filter(status='accepted').count(),
        'total_views': jobs.aggregate(Sum('views_count'))['views_count__sum'] or 0,
        'active_countries': agency.active_countries.count(),
        'is_verified': agency.is_verified,
        'license_valid': agency.is_license_valid() if hasattr(agency, 'is_license_valid') else False,
        'license_expiry': agency.license_expiry.strftime('%Y-%m-%d') if agency.license_expiry else None,
    }
    return JsonResponse(stats)


# ==============================================
# ADMIN AGENCY MANAGEMENT (for admin panel)
# ==============================================

@login_required
def admin_register_agency(request):
    """Admin register agency"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')
    
    if request.method == 'POST':
        form = AgencyRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'agency'
            user.status = 'approved'
            user.is_verified = True
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            RecruitmentAgency.objects.create(
                user=user,
                agency_name=form.cleaned_data.get('agency_name', ''),
                contact_email=user.email,
                contact_phone=user.phone_number,
                is_verified=True,
                verification_date=timezone.now(),
                license_expiry=timezone.now().date() + timedelta(days=365)  # ADDED: Default license expiry
            )
            
            messages.success(request, f'Agency {user.full_name} registered successfully!')
            return redirect('admin_panel:admin_agency_list')
    else:
        form = AgencyRegistrationForm()
    
    context = {'form': form}
    return render(request, 'admin_panel/agencies/register.html', context)


@login_required
def admin_agency_setup(request, agency_id):
    """Admin complete agency setup"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')
    
    agency = get_object_or_404(RecruitmentAgency, id=agency_id)
    
    if request.method == 'POST':
        form = AgencyProfileForm(request.POST, request.FILES, instance=agency)
        if form.is_valid():
            agency = form.save()
            
            if 'active_countries' in request.POST:
                country_ids = request.POST.getlist('active_countries')
                agency.active_countries.set(country_ids)
            
            messages.success(request, f'Agency {agency.agency_name} profile updated!')
            return redirect('admin_panel:admin_agency_detail', agency_id=agency_id)
    else:
        form = AgencyProfileForm(instance=agency)
    
    countries = Country.objects.filter(is_active=True)
    
    context = {
        'form': form,
        'agency': agency,
        'countries': countries,
    }
    return render(request, 'admin_panel/agencies/setup.html', context)


@login_required
def admin_agency_stats(request, agency_id):
    """Get agency statistics for admin (AJAX)"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied.'}, status=403)
    
    agency = get_object_or_404(RecruitmentAgency, id=agency_id)
    
    jobs = Job.objects.filter(agency=agency)
    applications = JobApplication.objects.filter(job__agency=agency)
    agency_applications = AgencyApplication.objects.filter(agency=agency)
    
    stats = {
        'agency_name': agency.agency_name,
        'is_verified': agency.is_verified,
        'verification_date': agency.verification_date.strftime('%Y-%m-%d') if agency.verification_date else None,
        'license_valid': agency.is_license_valid() if hasattr(agency, 'is_license_valid') else False,
        'license_expiry': agency.license_expiry.strftime('%Y-%m-%d') if agency.license_expiry else None,
        'total_jobs': jobs.count(),
        'active_jobs': jobs.filter(status='active').count(),
        'pending_jobs': jobs.filter(status='pending').count(),
        'total_applications': applications.count(),
        'agency_applications': agency_applications.count(),
        'placements': agency_applications.filter(status='accepted').count(),
        'active_countries': agency.active_countries.count(),
    }
    return JsonResponse(stats)


def agency_jobs_api(request, agency_id):
    """API endpoint for agency jobs"""
    agency = get_object_or_404(RecruitmentAgency, id=agency_id, is_verified=True)
    
    jobs = Job.objects.filter(
        agency=agency,
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