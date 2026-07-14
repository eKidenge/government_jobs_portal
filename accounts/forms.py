"""
Accounts App Forms
Handles user registration, login, profile updates, etc.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
import re

from .models import User, UserProfile

User = get_user_model()


class CitizenRegistrationForm(forms.ModelForm):
    """Form for citizen registration"""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
            'placeholder': 'Enter password'
        }),
        help_text='Minimum 8 characters with at least one number and special character'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
            'placeholder': 'Confirm password'
        }),
        label='Confirm Password'
    )
    
    # Document uploads
    cv = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'file-input',
            'accept': '.pdf,.doc,.docx'
        })
    )
    national_id_document = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'file-input',
            'accept': '.pdf,.jpg,.jpeg,.png'
        })
    )
    passport_document = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'file-input',
            'accept': '.pdf,.jpg,.jpeg,.png'
        })
    )
    photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'file-input',
            'accept': '.jpg,.jpeg,.png'
        })
    )
    academic_certificates = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'file-input',
            'accept': '.pdf,.jpg,.jpeg,.png'
        })
    )
    professional_certificates = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'file-input',
            'accept': '.pdf,.jpg,.jpeg,.png'
        })
    )
    cover_letter = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'file-input',
            'accept': '.pdf,.doc,.docx'
        })
    )
    
    class Meta:
        model = User
        fields = [
            'national_id', 'full_name', 'date_of_birth', 'gender',
            'phone_number', 'email', 'county'
        ]
        widgets = {
            'national_id': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'placeholder': 'e.g., 12345678'
            }),
            'full_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'placeholder': 'John Doe'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'type': 'date'
            }),
            'gender': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent'
            }, choices=[('', 'Select Gender'), ('M', 'Male'), ('F', 'Female'), ('O', 'Other')]),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'placeholder': 'e.g., 0712345678'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'placeholder': 'john@example.com'
            }),
            'county': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'placeholder': 'e.g., Nairobi'
            }),
        }
    
    def clean_national_id(self):
        national_id = self.cleaned_data.get('national_id')
        if User.objects.filter(national_id=national_id).exists():
            raise ValidationError('This National ID is already registered.')
        if not national_id or len(national_id) < 6:
            raise ValidationError('Please enter a valid National ID.')
        return national_id
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        return email
    
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone or len(phone) < 10:
            raise ValidationError('Please enter a valid phone number.')
        # Remove any non-digit characters
        phone = re.sub(r'\D', '', phone)
        if len(phone) < 10:
            raise ValidationError('Please enter a valid phone number with at least 10 digits.')
        return phone
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one number.')
        if not re.search(r'[^a-zA-Z0-9]', password):
            raise ValidationError('Password must contain at least one special character.')
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        
        if password and password2 and password != password2:
            self.add_error('password2', 'Passwords do not match.')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.user_type = 'citizen'
        user.status = 'pending'
        
        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.create(
                user=user,
                cv=self.cleaned_data.get('cv'),
                national_id_document=self.cleaned_data.get('national_id_document'),
                passport_document=self.cleaned_data.get('passport_document'),
                photo=self.cleaned_data.get('photo'),
                cover_letter=self.cleaned_data.get('cover_letter')
            )
        
        return user


class LoginForm(forms.Form):
    """User login form"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
            'placeholder': 'Enter your email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
            'placeholder': 'Enter your password'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        
        if email and password:
            # User validation will be done in the view
            pass
        
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    """User profile update form"""
    
    class Meta:
        model = UserProfile
        fields = [
            'cv', 'national_id_document', 'passport_document', 'photo',
            'cover_letter', 'education', 'work_experience', 'skills',
            'languages', 'certifications', 'bio', 'linkedin_url', 'website'
        ]
        widgets = {
            'education': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'rows': 4,
                'placeholder': 'List your education history...'
            }),
            'work_experience': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'rows': 4,
                'placeholder': 'List your work experience...'
            }),
            'skills': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'rows': 3,
                'placeholder': 'List your skills (comma separated)...'
            }),
            'languages': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'rows': 2,
                'placeholder': 'List languages you speak...'
            }),
            'certifications': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'rows': 3,
                'placeholder': 'List your certifications...'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'rows': 4,
                'placeholder': 'Tell us about yourself...'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'placeholder': 'https://linkedin.com/in/username'
            }),
            'website': forms.URLInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
                'placeholder': 'https://yourwebsite.com'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


class EmployerRegistrationForm(forms.ModelForm):
    """Form for employer registration"""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent'
        }),
        label='Confirm Password'
    )
    
    class Meta:
        model = User
        fields = ['email', 'full_name', 'phone_number']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        return email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        
        if password and password2 and password != password2:
            self.add_error('password2', 'Passwords do not match.')
        
        return cleaned_data


class AgencyRegistrationForm(forms.ModelForm):
    """Form for recruitment agency registration"""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent'
        }),
        label='Confirm Password'
    )
    
    class Meta:
        model = User
        fields = ['email', 'full_name', 'phone_number']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        return email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        
        if password and password2 and password != password2:
            self.add_error('password2', 'Passwords do not match.')
        
        return cleaned_data


class PasswordChangeForm(forms.Form):
    """Password change form"""
    
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
            'placeholder': 'Enter current password'
        }),
        label='Current Password'
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
            'placeholder': 'Enter new password'
        }),
        label='New Password',
        help_text='Minimum 8 characters with at least one number and special character'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
            'placeholder': 'Confirm new password'
        }),
        label='Confirm New Password'
    )
    
    def clean_new_password(self):
        password = self.cleaned_data.get('new_password')
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one number.')
        if not re.search(r'[^a-zA-Z0-9]', password):
            raise ValidationError('Password must contain at least one special character.')
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        
        return cleaned_data


class PasswordResetRequestForm(forms.Form):
    """Password reset request form"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
            'placeholder': 'Enter your email address'
        })
    )


class PasswordResetConfirmForm(forms.Form):
    """Password reset confirmation form"""
    
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
            'placeholder': 'Enter new password'
        }),
        label='New Password',
        help_text='Minimum 8 characters with at least one number and special character'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-light focus:border-transparent',
            'placeholder': 'Confirm new password'
        }),
        label='Confirm New Password'
    )
    
    def clean_new_password(self):
        password = self.cleaned_data.get('new_password')
        if len(password) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one number.')
        if not re.search(r'[^a-zA-Z0-9]', password):
            raise ValidationError('Password must contain at least one special character.')
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        
        return cleaned_data