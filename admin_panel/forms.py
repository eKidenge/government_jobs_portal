"""
Admin Panel Forms
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from accounts.models import User
from employers.models import EmployerProfile
from jobs.models import Job, Category, Country
from agencies.models import RecruitmentAgency
from payments.models import Payment, PaymentPlan


class AdminJobForm(forms.ModelForm):
    """Form for creating/editing jobs in admin"""
    
    class Meta:
        model = Job
        fields = [
            'title', 'employer', 'agency', 'country', 'category',
            'description', 'responsibilities', 'requirements', 'benefits',
            'salary_min', 'salary_max', 'salary_currency', 'is_salary_negotiable',
            'employment_type', 'experience_level', 'location', 'is_remote',
            'visa_requirements', 'required_languages', 'closing_date',
            'is_featured', 'status'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'responsibilities': forms.Textarea(attrs={'rows': 5}),
            'requirements': forms.Textarea(attrs={'rows': 5}),
            'benefits': forms.Textarea(attrs={'rows': 3}),
            'visa_requirements': forms.Textarea(attrs={'rows': 3}),
            'required_languages': forms.Textarea(attrs={'rows': 2, 'placeholder': 'e.g., English, French, Swahili'}),
            'closing_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        employer = cleaned_data.get('employer')
        agency = cleaned_data.get('agency')
        
        # At least one of employer or agency must be specified
        if not employer and not agency:
            raise ValidationError('Please specify either an employer or a recruitment agency.')
        
        # Only one can be specified
        if employer and agency:
            raise ValidationError('Please specify only one: either an employer OR a recruitment agency.')
        
        # Validate closing date
        closing_date = cleaned_data.get('closing_date')
        if closing_date and closing_date <= timezone.now():
            raise ValidationError('Closing date must be in the future.')
        
        # Validate salary range
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')
        
        if salary_min and salary_max and salary_min > salary_max:
            raise ValidationError('Minimum salary cannot be greater than maximum salary.')
        
        return cleaned_data


class AdminEmployerForm(forms.ModelForm):
    """Form for editing employers in admin"""
    
    class Meta:
        model = EmployerProfile
        fields = [
            'company_name', 'registration_number', 'license_number',
            'country', 'website', 'description', 'industry',
            'company_size', 'address', 'contact_phone', 'contact_email',
            'is_verified'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean_license_number(self):
        license_number = self.cleaned_data.get('license_number')
        if EmployerProfile.objects.filter(license_number=license_number).exclude(id=self.instance.id).exists():
            raise ValidationError('This license number is already registered.')
        return license_number


class AdminAgencyForm(forms.ModelForm):
    """Form for editing recruitment agencies in admin"""
    
    class Meta:
        model = RecruitmentAgency
        fields = [
            'agency_name', 'registration_number', 'license_number',
            'license_expiry', 'country', 'website', 'description',
            'address', 'contact_phone', 'contact_email',
            'is_verified', 'specializations'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'specializations': forms.Textarea(attrs={'rows': 2, 'placeholder': 'e.g., ICT, Healthcare, Engineering'}),
            'license_expiry': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_license_number(self):
        license_number = self.cleaned_data.get('license_number')
        if RecruitmentAgency.objects.filter(license_number=license_number).exclude(id=self.instance.id).exists():
            raise ValidationError('This license number is already registered.')
        return license_number
    
    def clean_license_expiry(self):
        license_expiry = self.cleaned_data.get('license_expiry')
        if license_expiry and license_expiry < timezone.now().date():
            raise ValidationError('License expiry date must be in the future.')
        return license_expiry


class AdminUserForm(forms.ModelForm):
    """Form for editing users in admin"""
    
    new_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'placeholder': 'Leave blank to keep current password'}),
        help_text='Set a new password for the user (optional).'
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'full_name', 'national_id', 'passport_number',
            'date_of_birth', 'gender', 'phone_number', 'county',
            'user_type', 'status', 'is_verified', 'is_active'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise ValidationError('This email is already registered.')
        return email
    
    def clean_national_id(self):
        national_id = self.cleaned_data.get('national_id')
        if User.objects.filter(national_id=national_id).exclude(id=self.instance.id).exists():
            raise ValidationError('This National ID is already registered.')
        return national_id
    
    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Set new password if provided
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.set_password(new_password)
        
        if commit:
            user.save()
        return user


class AdminPaymentForm(forms.ModelForm):
    """Form for managing payments in admin"""
    
    class Meta:
        model = Payment
        fields = [
            'user', 'plan', 'amount', 'currency',
            'payment_method', 'status', 'transaction_reference'
        ]
    
    def clean_transaction_reference(self):
        reference = self.cleaned_data.get('transaction_reference')
        if Payment.objects.filter(transaction_reference=reference).exclude(id=self.instance.id).exists():
            raise ValidationError('This transaction reference is already used.')
        return reference


class AdminSettingsForm(forms.Form):
    """Form for system settings"""
    
    site_name = forms.CharField(max_length=100, required=True)
    site_url = forms.URLField(required=True)
    admin_email = forms.EmailField(required=True)
    
    # Payment settings
    single_application_fee = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    monthly_access_fee = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    quarterly_access_fee = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    
    # Notification settings
    enable_email_notifications = forms.BooleanField(required=False)
    enable_sms_notifications = forms.BooleanField(required=False)
    
    # Security settings
    require_email_verification = forms.BooleanField(required=False, initial=True)
    max_login_attempts = forms.IntegerField(min_value=3, max_value=10, initial=5)
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate that fees are positive
        single_fee = cleaned_data.get('single_application_fee')
        monthly_fee = cleaned_data.get('monthly_access_fee')
        quarterly_fee = cleaned_data.get('quarterly_access_fee')
        
        if single_fee and single_fee <= 0:
            raise ValidationError('Application fee must be positive.')
        
        if monthly_fee and monthly_fee <= 0:
            raise ValidationError('Monthly fee must be positive.')
        
        if quarterly_fee and quarterly_fee <= 0:
            raise ValidationError('Quarterly fee must be positive.')
        
        return cleaned_data


class AdminBulkActionForm(forms.Form):
    """Form for bulk actions"""
    
    ACTION_CHOICES = [
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('delete', 'Delete'),
        ('feature', 'Feature'),
        ('unfeature', 'Unfeature'),
        ('activate', 'Activate'),
        ('suspend', 'Suspend'),
    ]
    
    job_ids = forms.CharField(widget=forms.HiddenInput, required=False)
    user_ids = forms.CharField(widget=forms.HiddenInput, required=False)
    action = forms.ChoiceField(choices=ACTION_CHOICES, required=True)
    reason = forms.CharField(widget=forms.Textarea, required=False)
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        reason = cleaned_data.get('reason')
        
        if action in ['reject', 'suspend'] and not reason:
            raise ValidationError('Please provide a reason for this action.')
        
        return cleaned_data