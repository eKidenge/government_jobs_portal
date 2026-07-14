from django.db import models
from django.utils import timezone
import uuid
from accounts.models import User
from employers.models import EmployerProfile
from agencies.models import RecruitmentAgency


class Country(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=3, unique=True)
    flag = models.ImageField(upload_to='flags/', null=True, blank=True)
    currency = models.CharField(max_length=10, blank=True)
    currency_symbol = models.CharField(max_length=5, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'countries'
        ordering = ['name']
        verbose_name_plural = 'Countries'
    
    def __str__(self):
        return self.name


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Job(models.Model):
    EMPLOYMENT_TYPES = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('temporary', 'Temporary'),
        ('internship', 'Internship'),
        ('volunteer', 'Volunteer'),
        ('freelance', 'Freelance'),
    )
    
    EXPERIENCE_LEVELS = (
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('executive', 'Executive Level'),
    )
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('expired', 'Expired'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name='jobs', null=True, blank=True)
    agency = models.ForeignKey(RecruitmentAgency, on_delete=models.CASCADE, related_name='jobs', null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='jobs')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='jobs')
    
    # Job Details
    description = models.TextField()
    responsibilities = models.TextField()
    requirements = models.TextField()
    benefits = models.TextField(blank=True, null=True)
    
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=10, blank=True, default='KES')
    is_salary_negotiable = models.BooleanField(default=False)
    
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS)
    
    location = models.CharField(max_length=255)
    is_remote = models.BooleanField(default=False)
    
    # Visa & Requirements
    visa_requirements = models.TextField(blank=True, null=True)
    required_languages = models.JSONField(default=list, blank=True)
    
    # Dates
    posted_date = models.DateTimeField(auto_now_add=True)
    closing_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Metadata
    views_count = models.IntegerField(default=0)
    applications_count = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'jobs'
        ordering = ['-posted_date']
        indexes = [
            models.Index(fields=['status', 'closing_date']),
            models.Index(fields=['country', 'category']),
            models.Index(fields=['employer']),
            models.Index(fields=['agency']),
            models.Index(fields=['is_featured', 'is_verified']),
        ]
    
    def __str__(self):
        employer_name = self.employer.company_name if self.employer else None
        agency_name = self.agency.agency_name if self.agency else None
        source = employer_name or agency_name or 'N/A'
        return f"{self.title} at {source}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.closing_date
    
    def save(self, *args, **kwargs):
        if not self.is_verified and self.status == 'approved':
            self.is_verified = True
        super().save(*args, **kwargs)


class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('medical_examination', 'Medical Examination'),
        ('visa_processing', 'Visa Processing'),
        ('offer_extended', 'Offer Extended'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    cover_letter = models.TextField(blank=True)
    additional_documents = models.JSONField(default=list, blank=True)
    
    # Application tracking
    review_notes = models.TextField(blank=True, null=True)
    interview_date = models.DateTimeField(blank=True, null=True)
    interview_notes = models.TextField(blank=True, null=True)
    offered_salary = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    date_applied = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_status_changed = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'job_applications'
        ordering = ['-date_applied']
        unique_together = ['job', 'applicant']
        indexes = [
            models.Index(fields=['status', 'applicant']),
            models.Index(fields=['job']),
        ]
    
    def __str__(self):
        return f"{self.applicant.full_name} - {self.job.title}"