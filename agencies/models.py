"""
Recruitment Agencies App Models
"""
from django.db import models
from django.utils import timezone
import uuid
from accounts.models import User


class RecruitmentAgency(models.Model):
    """Recruitment Agency Profile Model"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agency_profile')
    
    # Basic Information
    agency_name = models.CharField(max_length=255)
    registration_number = models.CharField(max_length=50, unique=True)
    license_number = models.CharField(max_length=50, unique=True)
    license_expiry = models.DateField()
    
    # Location - Use string reference to avoid circular import
    country = models.ForeignKey('jobs.Country', on_delete=models.SET_NULL, null=True, related_name='agencies')
    address = models.TextField()
    
    # Contact
    contact_phone = models.CharField(max_length=15)
    contact_email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    
    # Description
    description = models.TextField()
    specializations = models.JSONField(default=list, blank=True)
    
    # Branding
    logo = models.ImageField(upload_to='agency_logos/', null=True, blank=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    accreditation_documents = models.JSONField(default=list, blank=True)
    
    # Active Countries - Use string reference to avoid circular import
    active_countries = models.ManyToManyField('jobs.Country', related_name='active_agencies', blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'recruitment_agencies'
        verbose_name_plural = 'Recruitment Agencies'
        ordering = ['agency_name']
        indexes = [
            models.Index(fields=['agency_name']),
            models.Index(fields=['license_number']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['license_expiry']),
        ]
    
    def __str__(self):
        return self.agency_name
    
    def is_license_valid(self):
        return timezone.now().date() <= self.license_expiry
    
    def get_active_jobs_count(self):
        from jobs.models import Job
        return Job.objects.filter(agency=self, status='active').count()
    
    def get_total_applications(self):
        from jobs.models import JobApplication
        return JobApplication.objects.filter(job__agency=self).count()


class AgencyDocument(models.Model):
    """Agency Accreditation Documents"""
    
    DOCUMENT_TYPES = (
        ('license', 'License Certificate'),
        ('registration', 'Registration Certificate'),
        ('accreditation', 'Accreditation Letter'),
        ('tax_compliance', 'Tax Compliance Certificate'),
        ('other', 'Other Document'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agency = models.ForeignKey(RecruitmentAgency, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document = models.FileField(upload_to='agency_documents/')
    description = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    verified_date = models.DateTimeField(null=True, blank=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'agency_documents'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.agency.agency_name} - {self.get_document_type_display()}"


class AgencyApplication(models.Model):
    """Track applications handled by agencies"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('submitted', 'Submitted to Employer'),
        ('interview', 'Interview Scheduled'),
        ('offer', 'Offer Extended'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agency = models.ForeignKey(RecruitmentAgency, on_delete=models.CASCADE, related_name='agency_applications')
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='agency_applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agency_applications')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    
    # Tracking
    submitted_to_employer_date = models.DateTimeField(null=True, blank=True)
    interview_date = models.DateTimeField(null=True, blank=True)
    offer_date = models.DateTimeField(null=True, blank=True)
    accepted_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'agency_applications'
        ordering = ['-created_at']
        unique_together = ['agency', 'job', 'applicant']
    
    def __str__(self):
        return f"{self.applicant.full_name} - {self.job.title} ({self.agency.agency_name})"


class AgencyContract(models.Model):
    """Contracts managed by agencies"""
    
    CONTRACT_TYPES = (
        ('employment', 'Employment Contract'),
        ('service', 'Service Agreement'),
        ('placement', 'Placement Agreement'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('signed', 'Signed'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('terminated', 'Terminated'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agency = models.ForeignKey(RecruitmentAgency, on_delete=models.CASCADE, related_name='contracts')
    application = models.ForeignKey(AgencyApplication, on_delete=models.CASCADE, related_name='contracts')
    
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPES)
    contract_file = models.FileField(upload_to='agency_contracts/')
    contract_number = models.CharField(max_length=100, unique=True)
    
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Financial details
    salary_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=10, default='KES')
    benefits = models.TextField(blank=True)
    
    # Signatures
    applicant_signed = models.BooleanField(default=False)
    applicant_signed_date = models.DateTimeField(null=True, blank=True)
    employer_signed = models.BooleanField(default=False)
    employer_signed_date = models.DateTimeField(null=True, blank=True)
    agency_signed = models.BooleanField(default=False)
    agency_signed_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'agency_contracts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.contract_number} - {self.application.applicant.full_name}"


class AgencyRecruitmentProcess(models.Model):
    """Track recruitment process stages for agencies"""
    
    STAGES = (
        ('sourcing', 'Candidate Sourcing'),
        ('screening', 'Screening'),
        ('interview', 'Interview'),
        ('reference_check', 'Reference Check'),
        ('document_verification', 'Document Verification'),
        ('employer_submission', 'Employer Submission'),
        ('employer_interview', 'Employer Interview'),
        ('offer', 'Offer Stage'),
        ('visa_processing', 'Visa Processing'),
        ('deployment', 'Deployment'),
        ('completed', 'Completed'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agency = models.ForeignKey(RecruitmentAgency, on_delete=models.CASCADE, related_name='processes')
    application = models.ForeignKey(AgencyApplication, on_delete=models.CASCADE, related_name='processes')
    
    stage = models.CharField(max_length=30, choices=STAGES, default='sourcing')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    notes = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_processes')
    
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'agency_recruitment_processes'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.agency.agency_name} - {self.get_stage_display()} - {self.application.applicant.full_name}"