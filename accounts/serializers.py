"""
Accounts Serializers
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'full_name', 'national_id', 'passport_number',
            'date_of_birth', 'gender', 'phone_number', 'county',
            'password', 'password2', 'user_type'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True},
            'user_type': {'required': False},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'national_id', 'passport_number',
            'date_of_birth', 'gender', 'phone_number', 'county',
            'user_type', 'status', 'is_verified', 'date_joined'
        ]
        read_only_fields = ['id', 'email', 'user_type', 'status', 'is_verified', 'date_joined']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user"""
    class Meta:
        model = User
        fields = [
            'full_name', 'national_id', 'passport_number',
            'date_of_birth', 'gender', 'phone_number', 'county'
        ]
    
    def validate_phone_number(self, value):
        if value and len(value) < 10:
            raise serializers.ValidationError("Phone number must be at least 10 digits.")
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""
    current_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Password fields didn't match."})
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Password fields didn't match."})
        return attrs


class UserProfileDetailSerializer(serializers.ModelSerializer):
    """Serializer for user profile with profile details"""
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'national_id', 'passport_number',
            'date_of_birth', 'gender', 'phone_number', 'county',
            'user_type', 'status', 'is_verified', 'date_joined', 'profile'
        ]
        read_only_fields = ['id', 'email', 'user_type', 'status', 'is_verified', 'date_joined']
    
    def get_profile(self, obj):
        try:
            profile = UserProfile.objects.get(user=obj)
            return {
                'cv': profile.cv.url if profile.cv else None,
                'national_id_document': profile.national_id_document.url if profile.national_id_document else None,
                'passport_document': profile.passport_document.url if profile.passport_document else None,
                'photo': profile.photo.url if profile.photo else None,
                'cover_letter': profile.cover_letter.url if profile.cover_letter else None,
                'education': profile.education,
                'work_experience': profile.work_experience,
                'skills': profile.skills,
                'languages': profile.languages,
                'certifications': profile.certifications,
                'bio': profile.bio,
                'linkedin_url': profile.linkedin_url,
                'website': profile.website,
            }
        except UserProfile.DoesNotExist:
            return None