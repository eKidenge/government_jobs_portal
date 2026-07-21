"""
Agencies App Forms
"""
from django import forms
from .models import RecruitmentAgency


class AgencyProfileForm(forms.ModelForm):
    """Form for agency profile update"""
    
    class Meta:
        model = RecruitmentAgency
        fields = [
            'agency_name',
            'registration_number',
            'license_number',
            'license_expiry',
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
    
    def clean_license_expiry(self):
        license_expiry = self.cleaned_data.get('license_expiry')
        if license_expiry and license_expiry < timezone.now().date():
            raise forms.ValidationError('License expiry date cannot be in the past.')
        return license_expiry