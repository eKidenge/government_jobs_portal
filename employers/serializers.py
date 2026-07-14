"""
Employers Serializers
"""
from rest_framework import serializers
from .models import EmployerProfile, EmployerDocument
from jobs.serializers import CountrySerializer


class EmployerDocumentSerializer(serializers.ModelSerializer):
    """Serializer for Employer Document"""
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    
    class Meta:
        model = EmployerDocument
        fields = [
            'id', 'document_type', 'document_type_display',
            'document', 'description', 'is_verified',
            'verified_date', 'uploaded_at'
        ]
        read_only_fields = ['id', 'uploaded_at']


class EmployerSerializer(serializers.ModelSerializer):
    """Serializer for Employer Profile (list view)"""
    country_name = serializers.CharField(source='country.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    job_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = EmployerProfile
        fields = [
            'id', 'company_name', 'country', 'country_name',
            'user_email', 'industry', 'company_size',
            'is_verified', 'logo', 'job_count',
            'created_at'
        ]


class EmployerDetailSerializer(serializers.ModelSerializer):
    """Serializer for Employer Profile (detail view)"""
    country = CountrySerializer(read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)
    user_phone = serializers.CharField(source='user.phone_number', read_only=True)
    documents = EmployerDocumentSerializer(many=True, read_only=True)
    job_count = serializers.SerializerMethodField()
    active_job_count = serializers.SerializerMethodField()
    total_applications = serializers.SerializerMethodField()
    
    class Meta:
        model = EmployerProfile
        fields = [
            'id', 'company_name', 'registration_number', 'license_number',
            'country', 'address', 'contact_phone', 'contact_email',
            'website', 'description', 'industry', 'company_size',
            'logo', 'is_verified', 'verification_date',
            'user_email', 'user_full_name', 'user_phone',
            'documents', 'job_count', 'active_job_count',
            'total_applications', 'created_at', 'updated_at'
        ]
    
    def get_job_count(self, obj):
        return obj.jobs.count()
    
    def get_active_job_count(self, obj):
        return obj.jobs.filter(status='active', closing_date__gte=timezone.now()).count()
    
    def get_total_applications(self, obj):
        from jobs.models import JobApplication
        return JobApplication.objects.filter(job__employer=obj).count()


class EmployerCreateSerializer(serializers.Serializer):
    """Serializer for creating employer"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, min_length=8)
    full_name = serializers.CharField(required=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    company_name = serializers.CharField(required=False, allow_blank=True)
    
    def validate_email(self, value):
        from accounts.models import User
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value


class EmployerUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating employer profile"""
    
    class Meta:
        model = EmployerProfile
        fields = [
            'company_name', 'registration_number', 'license_number',
            'country', 'address', 'contact_phone', 'contact_email',
            'website', 'description', 'industry', 'company_size'
        ]