"""
Agencies App Forms
"""
from django import forms
from django.utils import timezone
from .models import RecruitmentAgency
from jobs.models import Country


class AgencyProfileForm(forms.ModelForm):
    """Form for agency profile update"""
    
    class Meta:
        model = RecruitmentAgency
        fields = [
            'agency_name',
            'registration_number',
            'license_number',
            'license_expiry',
            'country',  # ADDED: This was missing
            'address',
            'contact_phone',
            'contact_email',
            'website',
            'description',
            'specializations',
            'logo',
            'active_countries',
        ]
        widgets = {
            'agency_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'placeholder': 'Enter agency name'
            }),
            'registration_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'placeholder': 'Enter business registration number'
            }),
            'license_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'placeholder': 'Enter agency license number'
            }),
            'license_expiry': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'type': 'date'
            }),
            'country': forms.Select(attrs={  # ADDED: Widget for country field
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'rows': 3,
                'placeholder': 'Enter agency physical address'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'placeholder': 'Enter contact phone number'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'placeholder': 'Enter contact email address'
            }),
            'website': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'placeholder': 'https://www.youragency.com'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'rows': 4,
                'placeholder': 'Describe your agency services and expertise'
            }),
            'specializations': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'rows': 3,
                'placeholder': 'List specializations (comma separated)'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent'
            }),
            'active_countries': forms.SelectMultiple(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make country field required and populate choices
        self.fields['country'].required = True
        self.fields['country'].queryset = Country.objects.filter(is_active=True)
        self.fields['country'].empty_label = "Select a country"
        
        # Make active_countries field optional
        self.fields['active_countries'].required = False
        self.fields['active_countries'].queryset = Country.objects.filter(is_active=True)
        self.fields['active_countries'].help_text = "Hold Ctrl/Cmd to select multiple countries"
    
    def clean_license_expiry(self):
        license_expiry = self.cleaned_data.get('license_expiry')
        if license_expiry and license_expiry < timezone.now().date():
            raise forms.ValidationError('License expiry date cannot be in the past.')
        return license_expiry
    
    def clean_registration_number(self):
        """Validate registration number uniqueness"""
        registration_number = self.cleaned_data.get('registration_number')
        if registration_number:
            qs = RecruitmentAgency.objects.filter(registration_number=registration_number)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('This registration number is already in use.')
        return registration_number
    
    def clean_license_number(self):
        """Validate license number uniqueness"""
        license_number = self.cleaned_data.get('license_number')
        if license_number:
            qs = RecruitmentAgency.objects.filter(license_number=license_number)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('This license number is already in use.')
        return license_number