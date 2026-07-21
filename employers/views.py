"""
Employers Views
Handles employer registration, profile management, and dashboard
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum  # Added Sum here
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET

from .models import EmployerProfile, EmployerDocument
from .forms import EmployerProfileForm, EmployerDocumentForm  # Added forms import
from accounts.models import User
from accounts.forms import EmployerRegistrationForm
from jobs.models import Job, JobApplication, Country
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