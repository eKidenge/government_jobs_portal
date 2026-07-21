"""
Jobs App Forms
Handles job search, application, and job creation forms
"""
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Job, JobApplication, Category, Country


class JobSearchForm(forms.Form):
    """Form for searching and filtering jobs"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
            'placeholder': 'Search jobs, keywords, or companies...'
        })
    )
    country = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent'
        })
    )
    category = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent'
        })
    )
    employment_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Types')] + list(Job.EMPLOYMENT_TYPES),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent'
        })
    )
    experience_level = forms.ChoiceField(
        required=False,
        choices=[('', 'All Levels')] + list(Job.EXPERIENCE_LEVELS),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent'
        })
    )
    salary_min = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
            'placeholder': 'Min'
        })
    )
    salary_max = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
            'placeholder': 'Max'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate country choices
        countries = Country.objects.filter(is_active=True).order_by('name')
        self.fields['country'].choices = [('', 'All Countries')] + [(str(c.id), c.name) for c in countries]
        
        # Populate category choices
        categories = Category.objects.filter(is_active=True).order_by('name')
        self.fields['category'].choices = [('', 'All Categories')] + [(str(c.id), c.name) for c in categories]
    
    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')
        
        if salary_min is not None and salary_max is not None:
            if salary_min > salary_max:
                self.add_error('salary_min', 'Minimum salary cannot be greater than maximum salary.')
        
        return cleaned_data


class JobApplicationForm(forms.ModelForm):
    """Form for applying to a job"""
    
    cover_letter = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'cover-letter-area',
            'rows': 8,
            'placeholder': 'Write a compelling cover letter explaining why you\'re the ideal candidate for this position...'
        }),
        help_text='Optional but highly recommended'
    )
    additional_documents = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'file-input',
            'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
        }),
        help_text='Upload any additional documents (PDF, DOC, DOCX, JPG, PNG)'
    )
    
    class Meta:
        model = JobApplication
        fields = ['cover_letter', 'additional_documents']
    
    def clean_additional_documents(self):
        file = self.cleaned_data.get('additional_documents')
        if file:
            # Check file size (max 5MB)
            if file.size > 5 * 1024 * 1024:
                raise ValidationError('File size must be less than 5MB.')
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            file_name = file.name.lower()
            if not any(file_name.endswith(ext) for ext in allowed_extensions):
                raise ValidationError('File type not supported. Please upload PDF, DOC, DOCX, JPG, or PNG.')
        
        return file


class JobForm(forms.ModelForm):
    """Form for creating/editing jobs (for employers and agencies)"""
    
    # Override the country and category fields to use ModelChoiceField
    country = forms.ModelChoiceField(
        queryset=Country.objects.filter(is_active=True).order_by('name'),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent'
        }),
        empty_label="Select Country",
        required=True
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True).order_by('name'),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent'
        }),
        empty_label="Select Category",
        required=True
    )
    
    class Meta:
        model = Job
        fields = [
            'title', 'country', 'category', 'description', 'responsibilities',
            'requirements', 'benefits', 'salary_min', 'salary_max',
            'salary_currency', 'is_salary_negotiable', 'employment_type',
            'experience_level', 'location', 'is_remote', 'visa_requirements',
            'required_languages', 'closing_date'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'placeholder': 'e.g., Senior Software Developer'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'rows': 6,
                'placeholder': 'Describe the job role and responsibilities...'
            }),
            'responsibilities': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'rows': 5,
                'placeholder': 'List key responsibilities...'
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'rows': 5,
                'placeholder': 'List requirements and qualifications...'
            }),
            'benefits': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'rows': 3,
                'placeholder': 'List benefits and perks...'
            }),
            'salary_min': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'placeholder': 'Minimum salary'
            }),
            'salary_max': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'placeholder': 'Maximum salary'
            }),
            'salary_currency': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent'
            }),
            'is_salary_negotiable': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-primary-light focus:ring-primary-light'
            }),
            'employment_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent'
            }),
            'experience_level': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'placeholder': 'e.g., Nairobi, Kenya'
            }),
            'is_remote': forms.CheckboxInput(attrs={
                'class': 'rounded border-gray-300 text-primary-light focus:ring-primary-light'
            }),
            'visa_requirements': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'rows': 3,
                'placeholder': 'List any visa requirements...'
            }),
            'required_languages': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'rows': 2,
                'placeholder': 'e.g., English, French, Swahili (comma separated)'
            }),
            'closing_date': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'type': 'datetime-local'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Currency choices
        self.fields['salary_currency'] = forms.ChoiceField(
            choices=[
                ('KES', 'KES - Kenyan Shilling'),
                ('USD', 'USD - US Dollar'),
                ('EUR', 'EUR - Euro'),
                ('GBP', 'GBP - British Pound'),
                ('CAD', 'CAD - Canadian Dollar'),
                ('AUD', 'AUD - Australian Dollar'),
                ('ZAR', 'ZAR - South African Rand'),
                ('UGX', 'UGX - Ugandan Shilling'),
                ('TZS', 'TZS - Tanzanian Shilling'),
                ('RWF', 'RWF - Rwandan Franc'),
            ],
            widget=forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent'
            })
        )
        
        # Set default currency
        if not self.instance.pk:
            self.fields['salary_currency'].initial = 'KES'
            # Set default closing date to 30 days from now
            self.fields['closing_date'].initial = timezone.now() + timezone.timedelta(days=30)
    
    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')
        closing_date = cleaned_data.get('closing_date')
        
        # Validate salary range
        if salary_min is not None and salary_max is not None:
            if salary_min > salary_max:
                self.add_error('salary_min', 'Minimum salary cannot be greater than maximum salary.')
        
        # Validate closing date
        if closing_date:
            if closing_date <= timezone.now():
                self.add_error('closing_date', 'Closing date must be in the future.')
        
        # Validate required languages - handle both string and list
        required_languages = cleaned_data.get('required_languages')
        if required_languages:
            if isinstance(required_languages, str):
                # Convert comma-separated string to list
                languages = [lang.strip() for lang in required_languages.split(',') if lang.strip()]
                cleaned_data['required_languages'] = languages
            elif isinstance(required_languages, list):
                # Already a list, just clean empty values
                cleaned_data['required_languages'] = [lang.strip() for lang in required_languages if lang and lang.strip()]
        
        return cleaned_data


class JobBulkActionForm(forms.Form):
    """Form for bulk actions on jobs"""
    
    ACTION_CHOICES = [
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('delete', 'Delete'),
        ('feature', 'Feature'),
        ('unfeature', 'Unfeature'),
        ('close', 'Close'),
        ('reopen', 'Reopen'),
    ]
    
    job_ids = forms.CharField(widget=forms.HiddenInput, required=False)
    action = forms.ChoiceField(choices=ACTION_CHOICES, required=True)
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
            'rows': 3,
            'placeholder': 'Provide a reason for this action...'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        reason = cleaned_data.get('reason')
        job_ids = cleaned_data.get('job_ids')
        
        if not job_ids:
            self.add_error('job_ids', 'No jobs selected.')
        
        if action in ['reject', 'close'] and not reason:
            self.add_error('reason', 'Please provide a reason for this action.')
        
        return cleaned_data


class JobExportForm(forms.Form):
    """Form for exporting jobs"""
    
    EXPORT_FORMATS = [
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('pdf', 'PDF'),
    ]
    
    format = forms.ChoiceField(choices=EXPORT_FORMATS, required=True)
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Status')] + list(Job.STATUS_CHOICES)
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            self.add_error('date_from', 'Start date cannot be after end date.')
        
        return cleaned_data