# employers/forms.py
from django import forms
from .models import EmployerProfile, EmployerDocument
from jobs.models import Country


class EmployerProfileForm(forms.ModelForm):
    """Form for employer profile creation and update"""
    
    class Meta:
        model = EmployerProfile
        fields = [
            'company_name',
            'registration_number',
            'license_number',
            'country',
            'address',
            'contact_phone',
            'contact_email',
            'website',
            'description',
            'industry',
            'company_size',
            'logo',
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter company name'
            }),
            'registration_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'e.g., KCB/2024/001'
            }),
            'license_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'e.g., KCB-LIC-001'
            }),
            'country': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Enter full address'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'e.g., +254-20-222-5678'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'info@company.com'
            }),
            'website': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'https://www.company.com'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 5,
                'placeholder': 'Describe your company, mission, and values'
            }),
            'industry': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'company_size': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': 'image/*'
            }),
        }
        labels = {
            'company_name': 'Company Name *',
            'registration_number': 'Registration Number *',
            'license_number': 'License Number *',
            'country': 'Country *',
            'address': 'Address *',
            'contact_phone': 'Contact Phone *',
            'contact_email': 'Contact Email *',
            'website': 'Website',
            'description': 'Company Description',
            'industry': 'Industry *',
            'company_size': 'Company Size *',
            'logo': 'Company Logo',
        }
        help_texts = {
            'registration_number': 'Your business registration number (must be unique)',
            'license_number': 'Your business license number (must be unique)',
            'logo': 'Recommended size: 200x200px (PNG, JPG, JPEG)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make certain fields required
        self.fields['company_name'].required = True
        self.fields['registration_number'].required = True
        self.fields['license_number'].required = True
        self.fields['country'].required = True
        self.fields['address'].required = True
        self.fields['contact_phone'].required = True
        self.fields['contact_email'].required = True
        self.fields['industry'].required = True
        self.fields['company_size'].required = True
        
        # Add country choices
        from jobs.models import Country
        self.fields['country'].queryset = Country.objects.filter(is_active=True)
        
        # Add empty label for optional fields
        self.fields['website'].required = False
        self.fields['description'].required = False
        self.fields['logo'].required = False
    
    def clean_registration_number(self):
        """Validate registration number uniqueness"""
        registration_number = self.cleaned_data.get('registration_number')
        if registration_number:
            # Check if another employer has this registration number
            qs = EmployerProfile.objects.filter(registration_number=registration_number)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('This registration number is already in use.')
        return registration_number
    
    def clean_license_number(self):
        """Validate license number uniqueness"""
        license_number = self.cleaned_data.get('license_number')
        if license_number:
            # Check if another employer has this license number
            qs = EmployerProfile.objects.filter(license_number=license_number)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('This license number is already in use.')
        return license_number


class EmployerDocumentForm(forms.ModelForm):
    """Form for employer document upload"""
    
    class Meta:
        model = EmployerDocument
        fields = ['document_type', 'document', 'description']
        widgets = {
            'document_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'document': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Optional description of this document'
            }),
        }
        labels = {
            'document_type': 'Document Type *',
            'document': 'Document File *',
            'description': 'Description',
        }
        help_texts = {
            'document': 'Accepted formats: PDF, DOC, DOCX, JPG, PNG (Max 10MB)',
        }
    
    def clean_document(self):
        """Validate document file"""
        document = self.cleaned_data.get('document')
        if document:
            # Check file size (max 10MB)
            if document.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must be under 10MB.')
            
            # Check file extension
            valid_extensions = ['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png']
            ext = document.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError(
                    f'Invalid file type. Allowed types: {", ".join(valid_extensions)}'
                )
        return document


class EmployerSearchForm(forms.Form):
    """Form for searching employers"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Search by company name or description...'
        })
    )
    industry = forms.ChoiceField(
        required=False,
        choices=[('', 'All Industries')] + list(EmployerProfile.INDUSTRIES),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )
    country = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate country choices
        from jobs.models import Country
        self.fields['country'].choices = [('', 'All Countries')] + [
            (str(c.id), c.name) for c in Country.objects.filter(is_active=True)
        ]