"""
Jobs Serializers
"""
from rest_framework import serializers
from .models import Job, Category, Country, JobApplication


class CountrySerializer(serializers.ModelSerializer):
    """Serializer for Country model"""
    job_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Country
        fields = ['id', 'name', 'code', 'flag', 'currency', 'is_active', 'job_count']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    job_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'is_active', 'job_count']


class JobListSerializer(serializers.ModelSerializer):
    """Serializer for job list"""
    country_name = serializers.CharField(source='country.name', read_only=True)
    country_code = serializers.CharField(source='country.code', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    employer_name = serializers.SerializerMethodField()
    agency_name = serializers.SerializerMethodField()
    employment_type_display = serializers.CharField(source='get_employment_type_display', read_only=True)
    experience_level_display = serializers.CharField(source='get_experience_level_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'employer_name', 'agency_name', 'country_name', 'country_code',
            'category_name', 'description', 'requirements', 'salary_min', 'salary_max',
            'salary_currency', 'is_salary_negotiable', 'employment_type', 'employment_type_display',
            'experience_level', 'experience_level_display', 'location', 'is_remote',
            'posted_date', 'closing_date', 'views_count', 'applications_count',
            'is_featured', 'is_verified', 'is_expired', 'status'
        ]
    
    def get_employer_name(self, obj):
        return obj.employer.company_name if obj.employer else None
    
    def get_agency_name(self, obj):
        return obj.agency.agency_name if obj.agency else None


class JobDetailSerializer(serializers.ModelSerializer):
    """Serializer for job detail"""
    country = CountrySerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    employer_name = serializers.SerializerMethodField()
    agency_name = serializers.SerializerMethodField()
    employment_type_display = serializers.CharField(source='get_employment_type_display', read_only=True)
    experience_level_display = serializers.CharField(source='get_experience_level_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'employer_name', 'agency_name', 'country', 'category',
            'description', 'responsibilities', 'requirements', 'benefits',
            'salary_min', 'salary_max', 'salary_currency', 'is_salary_negotiable',
            'employment_type', 'employment_type_display', 'experience_level',
            'experience_level_display', 'location', 'is_remote',
            'visa_requirements', 'required_languages', 'posted_date', 'closing_date',
            'views_count', 'applications_count', 'is_featured', 'is_verified', 'is_expired', 'status'
        ]
    
    def get_employer_name(self, obj):
        return obj.employer.company_name if obj.employer else None
    
    def get_agency_name(self, obj):
        return obj.agency.agency_name if obj.agency else None


class JobApplicationSerializer(serializers.ModelSerializer):
    """Serializer for job application"""
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_employer = serializers.CharField(source='job.employer.company_name', read_only=True, default=None)
    job_country = serializers.CharField(source='job.country.name', read_only=True)
    applicant_name = serializers.CharField(source='applicant.full_name', read_only=True)
    applicant_email = serializers.CharField(source='applicant.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = JobApplication
        fields = [
            'id', 'job', 'job_title', 'job_employer', 'job_country',
            'applicant', 'applicant_name', 'applicant_email',
            'status', 'status_display', 'cover_letter',
            'review_notes', 'interview_date', 'interview_notes',
            'offered_salary', 'date_applied', 'date_updated', 'date_status_changed'
        ]
        read_only_fields = ['id', 'date_applied', 'date_updated', 'date_status_changed']


class JobApplicationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating job application"""
    
    class Meta:
        model = JobApplication
        fields = ['cover_letter', 'additional_documents']
    
    def validate(self, data):
        # Add validation if needed
        return data


class JobApplicationStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating application status"""
    status = serializers.ChoiceField(choices=JobApplication.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)