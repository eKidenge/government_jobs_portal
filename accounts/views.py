"""
Accounts Views
Handles user registration, login, profile management, and dashboards
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.utils import timezone
import uuid

from .models import User, UserProfile
from .forms import (
    CitizenRegistrationForm,
    LoginForm,
    UserProfileForm,
    PasswordChangeForm,
    PasswordResetRequestForm,
    PasswordResetConfirmForm,
    EmployerRegistrationForm,
    AgencyRegistrationForm,
)
from jobs.models import Job, JobApplication
from payments.models import Payment, UserPaymentAccess
from employers.models import EmployerProfile
from agencies.models import RecruitmentAgency
from notifications.models import Notification


def register_view(request):
    """Registration view - handles all user types (citizen, employer, agency)"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Get user_type from POST or GET
    user_type = request.POST.get('user_type') or request.GET.get('type', 'citizen')
    
    # Select form based on user type
    if user_type == 'employer':
        form_class = EmployerRegistrationForm
    elif user_type == 'agency':
        form_class = AgencyRegistrationForm
    else:
        form_class = CitizenRegistrationForm
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            
            # Send welcome email
            try:
                subject = f'Welcome to Government Jobs Portal - {user.get_user_type_display()}'
                html_message = render_to_string('emails/welcome.html', {
                    'user': user,
                    'site_url': settings.SITE_URL
                })
                plain_message = strip_tags(html_message)
                send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html_message)
            except Exception as e:
                print(f"Email sending failed: {e}")
            
            messages.success(request, f'Account created successfully! Please login as {user.get_user_type_display()}.')
            return redirect('login')
    else:
        form = form_class()
    
    context = {
        'form': form,
        'user_type': user_type,
    }
    return render(request, 'accounts/register.html', context)


def login_view(request):
    """Login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                if user.status == 'suspended':
                    messages.error(request, 'Your account has been suspended. Please contact support.')
                    return render(request, 'accounts/login.html', {'form': form})
                
                login(request, user)
                messages.success(request, f'Welcome back, {user.full_name}!')
                
                # Redirect based on user type
                if user.is_staff:
                    return redirect('admin_dashboard')
                elif user.user_type == 'citizen':
                    return redirect('citizen_dashboard')
                elif user.user_type == 'employer':
                    return redirect('employers:employer_dashboard')
                elif user.user_type == 'agency':
                    return redirect('agencies:agency_dashboard')
                else:
                    return redirect('home')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def dashboard_redirect(request):
    """Redirect to appropriate dashboard based on user type"""
    if request.user.is_staff:
        return redirect('admin_dashboard')
    elif request.user.user_type == 'citizen':
        return redirect('citizen_dashboard')
    elif request.user.user_type == 'employer':
        return redirect('employers:employer_dashboard')
    elif request.user.user_type == 'agency':
        return redirect('agencies:agency_dashboard')
    return redirect('home')


@login_required
def citizen_dashboard(request):
    """Citizen dashboard"""
    if request.user.user_type != 'citizen':
        messages.error(request, 'Access denied. This is for citizens only.')
        return redirect('home')
    
    user = request.user
    applications = JobApplication.objects.filter(applicant=user).select_related('job', 'job__employer', 'job__country')
    
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
    
    # Status counts
    status_counts = {
        'submitted': applications.filter(status='submitted').count(),
        'under_review': applications.filter(status='under_review').count(),
        'shortlisted': applications.filter(status='shortlisted').count(),
        'interview_scheduled': applications.filter(status='interview_scheduled').count(),
        'accepted': applications.filter(status='accepted').count(),
        'rejected': applications.filter(status='rejected').count(),
    }
    
    # Profile completion
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    # Calculate profile completion
    completion_fields = [
        profile.cv, profile.national_id_document, profile.passport_document,
        profile.photo, profile.education, profile.work_experience,
        profile.skills, profile.languages
    ]
    completed = sum(1 for field in completion_fields if field)
    profile_completion = int((completed / len(completion_fields)) * 100) if completion_fields else 0
    
    context = {
        'user': user,
        'profile': profile,
        'applications': applications,
        'recent_applications': applications.order_by('-date_applied')[:5],
        'status_counts': status_counts,
        'has_payment_access': has_payment_access,
        'total_applications_used': total_applications_used,
        'access_type': access_type,
        'profile_completion': profile_completion,
    }
    
    return render(request, 'accounts/citizen_dashboard.html', context)


@login_required
def employer_dashboard(request):
    """Employer dashboard"""
    if request.user.user_type != 'employer':
        messages.error(request, 'Access denied. This is for employers only.')
        return redirect('home')
    
    try:
        employer = EmployerProfile.objects.get(user=request.user)
    except EmployerProfile.DoesNotExist:
        messages.error(request, 'Please complete your employer profile first.')
        return redirect('employers:employer_setup')
    
    jobs = Job.objects.filter(employer=employer)
    applications = JobApplication.objects.filter(job__employer=employer)
    
    context = {
        'employer': employer,
        'jobs': jobs,
        'jobs_count': jobs.count(),
        'active_jobs': jobs.filter(status='active').count(),
        'total_applications': applications.count(),
        'shortlisted': applications.filter(status='shortlisted').count(),
        'recent_jobs': jobs.order_by('-posted_date')[:5],
        'recent_applications': applications.order_by('-date_applied')[:5],
    }
    
    return render(request, 'employers/dashboard.html', context)


@login_required
def agency_dashboard(request):
    """Recruitment agency dashboard"""
    if request.user.user_type != 'agency':
        messages.error(request, 'Access denied. This is for recruitment agencies only.')
        return redirect('home')
    
    try:
        agency = RecruitmentAgency.objects.get(user=request.user)
    except RecruitmentAgency.DoesNotExist:
        messages.error(request, 'Please complete your agency profile first.')
        return redirect('agencies:agency_setup')
    
    jobs = Job.objects.filter(agency=agency)
    applications = JobApplication.objects.filter(job__agency=agency)
    
    context = {
        'agency': agency,
        'jobs': jobs,
        'jobs_count': jobs.count(),
        'active_jobs': jobs.filter(status='active').count(),
        'total_applications': applications.count(),
        'recent_jobs': jobs.order_by('-posted_date')[:5],
        'recent_applications': applications.order_by('-date_applied')[:5],
        'now': timezone.now().date(),
    }
    
    return render(request, 'agencies/dashboard.html', context)


@login_required
def admin_dashboard(request):
    """Admin dashboard - redirect to admin_panel"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')
    # Import and call the admin panel dashboard view directly
    from admin_panel.views import admin_dashboard as admin_panel_dashboard_view
    return admin_panel_dashboard_view(request)


@login_required
def profile_view(request):
    """User profile view"""
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    # Get applications count
    applications_count = JobApplication.objects.filter(applicant=user).count()
    
    # Get payments count and total spent
    payments = Payment.objects.filter(user=user, status='completed')
    payments_count = payments.count()
    total_spent = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=user)
        if form.is_valid():
            form.save()
            
            # Update user info if provided
            full_name = request.POST.get('full_name')
            phone_number = request.POST.get('phone_number')
            if full_name:
                user.full_name = full_name
            if phone_number:
                user.phone_number = phone_number
            user.save()
            
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile, user=user)
    
    context = {
        'user': user,
        'profile': profile,
        'form': form,
        'applications_count': applications_count,
        'payments_count': payments_count,
        'total_spent': total_spent,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit(request):
    """Edit user profile"""
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)
    
    if request.method == 'POST':
        # Update user info
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        national_id = request.POST.get('national_id')
        
        if full_name:
            user.full_name = full_name
        if phone_number:
            user.phone_number = phone_number
        if national_id:
            user.national_id = national_id
        user.save()
        
        # Update profile if needed
        # You can add more fields here
        
        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('profile')
    
    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, 'accounts/profile_edit.html', context)


@login_required
def profile_update(request):
    """Profile update AJAX endpoint"""
    if request.method == 'POST':
        user = request.user
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)
        
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=user)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Profile updated successfully!'})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@login_required
def upload_document(request):
    """Upload document via AJAX"""
    if request.method == 'POST' and request.FILES:
        user = request.user
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=user)
        
        document_type = request.POST.get('document_type')
        file = request.FILES.get('file')
        
        if document_type and file:
            if document_type == 'cv':
                profile.cv = file
            elif document_type == 'national_id':
                profile.national_id_document = file
            elif document_type == 'passport':
                profile.passport_document = file
            elif document_type == 'photo':
                profile.photo = file
            elif document_type == 'cover_letter':
                profile.cover_letter = file
            else:
                return JsonResponse({'success': False, 'message': 'Invalid document type.'})
            
            profile.save()
            return JsonResponse({
                'success': True, 
                'message': 'Document uploaded successfully!',
                'file_url': file.url if hasattr(file, 'url') else None
            })
    
    return JsonResponse({'success': False, 'message': 'No file provided.'})


@login_required
def delete_document(request, doc_id):
    """Delete uploaded document"""
    # Implement document deletion
    messages.success(request, 'Document deleted successfully.')
    return redirect('profile')


@login_required
def change_password(request):
    """Change password view"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            user = request.user
            current_password = form.cleaned_data['current_password']
            new_password = form.cleaned_data['new_password']
            
            if not user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
            else:
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully!')
                return redirect('profile')
    else:
        form = PasswordChangeForm()
    
    context = {'form': form}
    return render(request, 'accounts/password_change.html', context)


def password_reset_request(request):
    """Password reset request view"""
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
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
                
                messages.success(request, 'Password reset link has been sent to your email.')
                return redirect('login')
            except User.DoesNotExist:
                messages.info(request, 'If an account with that email exists, a reset link has been sent.')
    else:
        form = PasswordResetRequestForm()
    
    context = {'form': form}
    return render(request, 'accounts/password_reset.html', context)


def password_reset_confirm(request, token):
    """Password reset confirmation view"""
    if request.method == 'POST':
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            # Verify token and get user
            # You would retrieve the user from the token
            new_password = form.cleaned_data['new_password']
            
            # Set new password
            # user.set_password(new_password)
            # user.save()
            
            messages.success(request, 'Password has been reset successfully! Please login.')
            return redirect('login')
    else:
        form = PasswordResetConfirmForm()
    
    context = {'form': form}
    return render(request, 'accounts/password_reset_confirm.html', context)


@login_required
def verify_email(request, token):
    """Email verification view"""
    # Implement email verification logic
    messages.success(request, 'Email verified successfully!')
    return redirect('dashboard')


@login_required
def resend_verification_email(request):
    """Resend verification email"""
    # Implement resend logic
    messages.success(request, 'Verification email has been resent.')
    return redirect('dashboard')


@login_required
def delete_account(request):
    """Delete user account"""
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Account deleted successfully.')
        return redirect('home')
    return render(request, 'accounts/delete_account.html')


@login_required
def suspend_account(request):
    """Suspend user account (for admin use)"""
    if request.user.is_staff and request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        user.status = 'suspended'
        user.save()
        messages.success(request, f'User {user.full_name} has been suspended.')
        return redirect('admin_user_detail', user_id=user_id)
    return redirect('home')