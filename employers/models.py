"""
Employers App Models
"""
from django.db import models
from django.utils import timezone
import uuid
from accounts.models import User


class EmployerProfile(models.Model):
    """Employer Profile Model"""
    
    COMPANY_SIZES = (
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('500+', '500+ employees'),
    )
    
    INDUSTRIES = (
        ('agriculture', 'Agriculture'),
        ('construction', 'Construction'),
        ('education', 'Education'),
        ('finance', 'Finance'),
        ('government', 'Government'),
        ('healthcare', 'Healthcare'),
        ('hospitality', 'Hospitality'),
        ('ict', 'ICT'),
        ('manufacturing', 'Manufacturing'),
        ('transport', 'Transport & Logistics'),
        ('other', 'Other'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    
    # Basic Information
    company_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=50, unique=True)
    license_number = models.CharField(max_length=50, unique=True)
    
    # Location - Use string reference to avoid circular import
    country = models.ForeignKey('jobs.Country', on_delete=models.SET_NULL, null=True, related_name='employers')
    address = models.TextField()
    
    # Contact
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    
    # Description
    description = models.TextField(blank=True)
    industry = models.CharField(max_length=50, choices=INDUSTRIES)
    company_size = models.CharField(max_length=20, choices=COMPANY_SIZES)
    
    # Branding
    logo = models.ImageField(upload_to='employer_logos/', null=True, blank=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    verification_documents = models.JSONField(default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employer_profiles'
        ordering = ['company_name']
        indexes = [
            models.Index(fields=['company_name']),
            models.Index(fields=['license_number']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['industry']),
        ]
    
    def __str__(self):
        return self.company_name
    
    def get_active_jobs_count(self):
        from jobs.models import Job
        return Job.objects.filter(employer=self, status='active').count()
    
    def get_total_applications(self):
        from jobs.models import JobApplication
        return JobApplication.objects.filter(job__employer=self).count()


class EmployerDocument(models.Model):
    """Employer Verification Documents"""
    
    DOCUMENT_TYPES = (
        ('registration', 'Registration Certificate'),
        ('license', 'Business License'),
        ('tax_compliance', 'Tax Compliance Certificate'),
        ('other', 'Other Document'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document = models.FileField(upload_to='employer_documents/')
    description = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    verified_date = models.DateTimeField(null=True, blank=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employer_documents'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.employer.company_name} - {self.get_document_type_display()}"