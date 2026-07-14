from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email)
        
        # Set default values for required fields if not provided
        if 'date_of_birth' not in extra_fields:
            extra_fields.setdefault('date_of_birth', timezone.now().date())
        if 'gender' not in extra_fields:
            extra_fields.setdefault('gender', 'M')
        if 'full_name' not in extra_fields:
            extra_fields.setdefault('full_name', email.split('@')[0] if email else 'User')
        if 'national_id' not in extra_fields:
            extra_fields.setdefault('national_id', f'ID-{uuid.uuid4().hex[:10].upper()}')
        if 'phone_number' not in extra_fields:
            extra_fields.setdefault('phone_number', '0000000000')
        if 'county' not in extra_fields:
            extra_fields.setdefault('county', 'Nairobi')
            
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('status', 'approved')
        extra_fields.setdefault('user_type', 'admin')
        
        # Set required fields for superuser
        extra_fields.setdefault('date_of_birth', timezone.now().date())
        extra_fields.setdefault('gender', 'M')
        extra_fields.setdefault('full_name', email.split('@')[0] if email else 'Admin')
        extra_fields.setdefault('national_id', f'SUPER-{uuid.uuid4().hex[:8].upper()}')
        extra_fields.setdefault('phone_number', '0000000000')
        extra_fields.setdefault('county', 'Nairobi')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPES = (
        ('citizen', 'Citizen'),
        ('employer', 'Employer'),
        ('agency', 'Recruitment Agency'),
        ('admin', 'Administrator'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('suspended', 'Suspended'),
        ('rejected', 'Rejected'),
    )
    
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    national_id = models.CharField(max_length=20, unique=True)
    passport_number = models.CharField(max_length=20, blank=True, null=True)
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=15)
    county = models.CharField(max_length=100)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='citizen')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'national_id', 'phone_number']
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email', 'status']),
            models.Index(fields=['national_id']),
            models.Index(fields=['user_type']),
        ]
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    def get_full_name(self):
        return self.full_name
    
    def get_short_name(self):
        return self.full_name.split()[0] if self.full_name else self.email


class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Documents
    cv = models.FileField(upload_to='documents/cv/', null=True, blank=True)
    national_id_document = models.FileField(upload_to='documents/id/', null=True, blank=True)
    passport_document = models.FileField(upload_to='documents/passport/', null=True, blank=True)
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)
    cover_letter = models.FileField(upload_to='documents/cover_letters/', null=True, blank=True)
    
    # Education (JSON field for flexibility)
    education = models.JSONField(default=list, blank=True)
    work_experience = models.JSONField(default=list, blank=True)
    skills = models.JSONField(default=list, blank=True)
    languages = models.JSONField(default=list, blank=True)
    certifications = models.JSONField(default=list, blank=True)
    
    # Additional Info
    bio = models.TextField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Fixed: Changed DateTimeFile to DateTimeField
    
    class Meta:
        db_table = 'user_profiles'
    
    def __str__(self):
        return f"Profile for {self.user.full_name}"