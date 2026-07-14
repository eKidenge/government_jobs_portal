"""
Agencies Serializers
"""
from rest_framework import serializers
from .models import RecruitmentAgency, AgencyDocument, AgencyApplication, AgencyContract, AgencyRecruitmentProcess
from jobs.models import Job
from jobs.serializers import CountrySerializer


class AgencyDocumentSerializer(serializers.ModelSerializer):
    """Serializer for Agency Document"""
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    
    class Meta:
        model = AgencyDocument
        fields = [
            'id', 'document_type', 'document_type_display',
            'document', 'description', 'is_verified',
            'verified_date', 'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_at']


class AgencyJobSerializer(serializers.ModelSerializer):
    """Serializer for Agency Jobs"""
    country_name = serializers.CharField(source='country.name', read_only=True)
    country_code = serializers.CharField(source='country.code', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    employment_type_display = serializers.CharField(source='get_employment_type_display', read_only=True)
    experience_level_display = serializers.CharField(source='get_experience_level_display', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Job
        fields = [
            'id', 'title', 'country', 'country_name', 'country_code',
            'category', 'category_name', 'description', 'requirements',
            'salary_min', 'salary_max', 'salary_currency',
            'is_salary_negotiable', 'employment_type', 'employment_type_display',
            'experience_level', 'experience_level_display', 'location',
            'is_remote', 'visa_requirements', 'required_languages',
            'posted_date', 'closing_date', 'views_count',
            'applications_count', 'is_featured', 'is_verified',
            'is_expired', 'status'
        ]


class AgencySerializer(serializers.ModelSerializer):
    """Serializer for Agency (list view)"""
    country_name = serializers.CharField(source='country.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    job_count = serializers.IntegerField(read_only=True)
    license_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = RecruitmentAgency
        fields = [
            'id', 'agency_name', 'country', 'country_name',
            'user_email', 'is_verified', 'logo',
            'license_number', 'license_expiry', 'license_valid',
            'job_count', 'created_at'
        ]
    
    def get_license_valid(self, obj):
        return obj.is_license_valid()


class AgencyDetailSerializer(serializers.ModelSerializer):
    """Serializer for Agency (detail view)"""
    country = CountrySerializer(read_only=True)
    active_countries = CountrySerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)
    user_phone = serializers.CharField(source='user.phone_number', read_only=True)
    documents = AgencyDocumentSerializer(many=True, read_only=True)
    job_count = serializers.SerializerMethodField()
    active_job_count = serializers.SerializerMethodField()
    total_applications = serializers.SerializerMethodField()
    license_valid = serializers.SerializerMethodField()
    
    class Meta:
        model = RecruitmentAgency
        fields = [
            'id', 'agency_name', 'registration_number', 'license_number',
            'license_expiry', 'license_valid', 'country', 'address',
            'contact_phone', 'contact_email', 'website',
            'description', 'specializations', 'logo',
            'is_verified', 'verification_date',
            'user_email', 'user_full_name', 'user_phone',
            'documents', 'active_countries',
            'job_count', 'active_job_count', 'total_applications',
            'created_at', 'updated_at'
        ]
    
    def get_job_count(self, obj):
        return obj.jobs.count()
    
    def get_active_job_count(self, obj):
        from django.utils import timezone
        return obj.jobs.filter(status='active', closing_date__gte=timezone.now()).count()
    
    def get_total_applications(self, obj):
        from jobs.models import JobApplication
        return JobApplication.objects.filter(job__agency=obj).count()
    
    def get_license_valid(self, obj):
        return obj.is_license_valid()


class AgencyCreateSerializer(serializers.Serializer):
    """Serializer for creating agency"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, min_length=8)
    full_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    agency_name = serializers.CharField(required=False, allow_blank=True)
    
    def validate_email(self, value):
        from accounts.models import User
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value


class AgencyUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating agency profile"""
    
    class Meta:
        model = RecruitmentAgency
        fields = [
            'agency_name', 'registration_number', 'license_number',
            'license_expiry', 'country', 'address',
            'contact_phone', 'contact_email', 'website',
            'description', 'specializations'
        ]


class AgencyApplicationSerializer(serializers.ModelSerializer):
    """Serializer for Agency Application"""
    applicant_name = serializers.CharField(source='applicant.full_name', read_only=True)
    applicant_email = serializers.CharField(source='applicant.email', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    job_country = serializers.CharField(source='job.country.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = AgencyApplication
        fields = [
            'id', 'agency', 'job', 'job_title', 'job_country',
            'applicant', 'applicant_name', 'applicant_email',
            'status', 'status_display', 'notes',
            'submitted_to_employer_date', 'interview_date',
            'offer_date', 'accepted_date',
            'created_at', 'updated_at'
        ]


class AgencyContractSerializer(serializers.ModelSerializer):
    """Serializer for Agency Contract"""
    contract_type_display = serializers.CharField(source='get_contract_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    applicant_name = serializers.CharField(source='application.applicant.full_name', read_only=True)
    
    class Meta:
        model = AgencyContract
        fields = [
            'id', 'agency', 'application', 'applicant_name',
            'contract_type', 'contract_type_display',
            'contract_file', 'contract_number',
            'start_date', 'end_date', 'status', 'status_display',
            'salary_amount', 'salary_currency', 'benefits',
            'applicant_signed', 'applicant_signed_date',
            'employer_signed', 'employer_signed_date',
            'agency_signed', 'agency_signed_date',
            'created_at', 'updated_at'
        ]


class AgencyRecruitmentProcessSerializer(serializers.ModelSerializer):
    """Serializer for Agency Recruitment Process"""
    stage_display = serializers.CharField(source='get_stage_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    applicant_name = serializers.CharField(source='application.applicant.full_name', read_only=True)
    
    class Meta:
        model = AgencyRecruitmentProcess
        fields = [
            'id', 'agency', 'application', 'applicant_name',
            'stage', 'stage_display', 'status', 'status_display',
            'notes', 'assigned_to', 'start_date', 'end_date', 'updated_at'
        ]