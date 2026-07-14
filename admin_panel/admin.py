"""
Admin Panel Admin Configuration
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from .models import SystemSetting, AdminActionLog, AdminNotification
from accounts.models import User, UserProfile
from employers.models import EmployerProfile  # Changed: Import from employers.models
from agencies.models import RecruitmentAgency  # Changed: Import from agencies.models
from jobs.models import Job, Category, Country, JobApplication
from payments.models import Payment, PaymentPlan


class CustomUserAdmin(UserAdmin):
    """Custom User Admin with enhanced display"""
    
    list_display = ('email', 'full_name', 'user_type', 'status', 'is_active', 
                   'is_verified', 'date_joined')  # REMOVED 'action_buttons'
    list_filter = ('user_type', 'status', 'is_active', 'is_verified', 'date_joined')
    search_fields = ('email', 'full_name', 'national_id', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {
            'fields': ('full_name', 'national_id', 'passport_number', 'date_of_birth', 
                      'gender', 'phone_number', 'county')
        }),
        ('Account Info', {
            'fields': ('user_type', 'status', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Verification', {
            'fields': ('is_verified', 'email_verified', 'phone_verified')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'national_id', 'password1', 'password2', 'user_type'),
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ['date_joined', 'last_login']
        return []
    
    # REMOVED action_buttons method entirely
    
    actions = ['approve_users', 'suspend_users', 'activate_users']
    
    def approve_users(self, request, queryset):
        updated = queryset.update(status='approved', is_verified=True)
        self.message_user(request, f"{updated} users approved successfully.")
    approve_users.short_description = "Approve selected users"
    
    def suspend_users(self, request, queryset):
        updated = queryset.update(status='suspended')
        self.message_user(request, f"{updated} users suspended.")
    suspend_users.short_description = "Suspend selected users"
    
    def activate_users(self, request, queryset):
        updated = queryset.update(status='approved')
        self.message_user(request, f"{updated} users activated.")
    activate_users.short_description = "Activate selected users"


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """Job Admin with enhanced management features"""
    
    list_display = ('title', 'employer_or_agency', 'country', 'category', 'status', 
                   'applications_count', 'closing_date', 'is_verified', 'is_featured')
    # REMOVED 'admin_actions'
    list_filter = ('status', 'is_verified', 'is_featured', 'employment_type', 
                  'experience_level', 'country', 'category')
    search_fields = ('title', 'description', 'requirements', 'employer__company_name', 
                    'agency__agency_name')
    readonly_fields = ('views_count', 'applications_count', 'created_at', 'updated_at', 
                      'posted_date')
    date_hierarchy = 'posted_date'
    
    fieldsets = (
        ('Job Information', {
            'fields': ('title', 'employer', 'agency', 'country', 'category', 
                      'description', 'responsibilities', 'requirements', 'benefits')
        }),
        ('Compensation', {
            'fields': ('salary_min', 'salary_max', 'salary_currency', 'is_salary_negotiable')
        }),
        ('Employment Details', {
            'fields': ('employment_type', 'experience_level', 'location', 'is_remote', 
                      'visa_requirements', 'required_languages')
        }),
        ('Status & Dates', {
            'fields': ('status', 'closing_date', 'is_featured', 'is_verified')
        }),
        ('Statistics', {
            'fields': ('views_count', 'applications_count'),
            'classes': ('collapse',)
        }),
        ('System Info', {
            'fields': ('created_at', 'updated_at', 'posted_date'),
            'classes': ('collapse',)
        }),
    )
    
    def employer_or_agency(self, obj):
        """Display employer or agency name"""
        if obj.employer:
            return obj.employer.company_name
        elif obj.agency:
            return obj.agency.agency_name
        return 'N/A'
    employer_or_agency.short_description = 'Employer/Agency'
    
    # REMOVED admin_actions method entirely
    
    actions = ['approve_jobs', 'reject_jobs', 'feature_jobs', 'unfeature_jobs', 'delete_jobs']
    
    def approve_jobs(self, request, queryset):
        count = queryset.update(status='approved', is_verified=True)
        self.message_user(request, f"{count} jobs approved successfully.")
    approve_jobs.short_description = "Approve selected jobs"
    
    def reject_jobs(self, request, queryset):
        count = queryset.update(status='rejected')
        self.message_user(request, f"{count} jobs rejected.")
    reject_jobs.short_description = "Reject selected jobs"
    
    def feature_jobs(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f"{count} jobs featured successfully.")
    feature_jobs.short_description = "Feature selected jobs"
    
    def unfeature_jobs(self, request, queryset):
        count = queryset.update(is_featured=False)
        self.message_user(request, f"{count} jobs unfeatured.")
    unfeature_jobs.short_description = "Unfeature selected jobs"
    
    def delete_jobs(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} jobs deleted.")
    delete_jobs.short_description = "Delete selected jobs"


@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    """Employer Profile Admin"""
    
    list_display = ('company_name', 'user', 'country', 'industry', 'is_verified', 
                   'verification_date', 'jobs_count')  # REMOVED 'admin_actions'
    list_filter = ('is_verified', 'industry', 'country', 'company_size')
    search_fields = ('company_name', 'registration_number', 'license_number', 
                    'user__email', 'user__full_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Company Information', {
            'fields': ('company_name', 'registration_number', 'license_number', 
                      'country', 'website', 'description', 'industry', 'company_size')
        }),
        ('Contact Information', {
            'fields': ('address', 'contact_phone', 'contact_email')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_date', 'verification_documents')
        }),
        ('System Info', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def jobs_count(self, obj):
        """Count jobs posted by employer"""
        return Job.objects.filter(employer=obj).count()
    jobs_count.short_description = 'Jobs Posted'
    
    # REMOVED admin_actions method entirely
    
    actions = ['verify_employers', 'suspend_employers', 'activate_employers']
    
    def verify_employers(self, request, queryset):
        count = queryset.update(is_verified=True, verification_date=timezone.now())
        self.message_user(request, f"{count} employers verified successfully.")
    verify_employers.short_description = "Verify selected employers"
    
    def suspend_employers(self, request, queryset):
        for employer in queryset:
            employer.user.status = 'suspended'
            employer.user.save()
        self.message_user(request, f"{queryset.count()} employers suspended.")
    suspend_employers.short_description = "Suspend selected employers"
    
    def activate_employers(self, request, queryset):
        for employer in queryset:
            employer.user.status = 'approved'
            employer.user.save()
        self.message_user(request, f"{queryset.count()} employers activated.")
    activate_employers.short_description = "Activate selected employers"


@admin.register(RecruitmentAgency)
class RecruitmentAgencyAdmin(admin.ModelAdmin):
    """Recruitment Agency Admin"""
    
    list_display = ('agency_name', 'user', 'country', 'is_verified', 'license_expiry', 
                   'verification_date', 'jobs_count')  # REMOVED 'admin_actions'
    list_filter = ('is_verified', 'country', 'created_at')
    search_fields = ('agency_name', 'registration_number', 'license_number', 
                    'user__email', 'user__full_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Agency Information', {
            'fields': ('agency_name', 'registration_number', 'license_number', 
                      'license_expiry', 'country', 'website', 'description', 'specializations')
        }),
        ('Contact Information', {
            'fields': ('address', 'contact_phone', 'contact_email')
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_date', 'accreditation_documents')
        }),
        ('Active Countries', {
            'fields': ('active_countries',)
        }),
        ('System Info', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ('active_countries',)
    
    def jobs_count(self, obj):
        """Count jobs posted by agency"""
        return Job.objects.filter(agency=obj).count()
    jobs_count.short_description = 'Jobs Posted'
    
    # REMOVED admin_actions method entirely
    
    actions = ['verify_agencies', 'suspend_agencies', 'activate_agencies']
    
    def verify_agencies(self, request, queryset):
        count = queryset.update(is_verified=True, verification_date=timezone.now())
        self.message_user(request, f"{count} agencies verified successfully.")
    verify_agencies.short_description = "Verify selected agencies"
    
    def suspend_agencies(self, request, queryset):
        for agency in queryset:
            agency.user.status = 'suspended'
            agency.user.save()
        self.message_user(request, f"{queryset.count()} agencies suspended.")
    suspend_agencies.short_description = "Suspend selected agencies"
    
    def activate_agencies(self, request, queryset):
        for agency in queryset:
            agency.user.status = 'approved'
            agency.user.save()
        self.message_user(request, f"{queryset.count()} agencies activated.")
    activate_agencies.short_description = "Activate selected agencies"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Payment Admin with management features"""
    
    list_display = ('transaction_reference', 'user', 'amount', 'currency', 'payment_method', 
                   'status', 'payment_date', 'plan')  # REMOVED 'admin_actions'
    list_filter = ('status', 'payment_method', 'payment_date', 'plan')
    search_fields = ('transaction_reference', 'user__email', 'user__full_name', 
                    'mpesa_receipt_number')
    readonly_fields = ('created_at', 'updated_at', 'payment_date')
    date_hierarchy = 'payment_date'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('user', 'plan', 'amount', 'currency', 'payment_method', 
                      'transaction_reference', 'status')
        }),
        ('M-Pesa Details', {
            'fields': ('mpesa_receipt_number', 'mpesa_phone_number'),
            'classes': ('collapse',)
        }),
        ('Bank Details', {
            'fields': ('bank_reference',),
            'classes': ('collapse',)
        }),
        ('Subscription Details', {
            'fields': ('subscription_start', 'subscription_end'),
            'classes': ('collapse',)
        }),
        ('System Info', {
            'fields': ('payment_date', 'completed_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    # REMOVED admin_actions method entirely
    
    actions = ['confirm_payments', 'refund_payments']
    
    def confirm_payments(self, request, queryset):
        from payments.views import grant_payment_access
        
        count = 0
        for payment in queryset:
            if payment.status == 'pending':
                payment.status = 'completed'
                payment.completed_date = timezone.now()
                payment.save()
                grant_payment_access(payment.user, payment)
                count += 1
        
        self.message_user(request, f"{count} payments confirmed successfully.")
    confirm_payments.short_description = "Confirm selected payments"
    
    def refund_payments(self, request, queryset):
        from payments.models import UserPaymentAccess
        
        count = 0
        for payment in queryset:
            if payment.status == 'completed':
                payment.status = 'refunded'
                payment.save()
                
                # Revoke access
                try:
                    access = UserPaymentAccess.objects.get(user=payment.user)
                    access.has_access = False
                    access.save()
                except UserPaymentAccess.DoesNotExist:
                    pass
                
                count += 1
        
        self.message_user(request, f"{count} payments refunded.")
    refund_payments.short_description = "Refund selected payments"


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    """Country Admin"""
    
    list_display = ('name', 'code', 'currency', 'is_active', 'jobs_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    ordering = ('name',)
    
    def jobs_count(self, obj):
        """Count jobs in this country"""
        return Job.objects.filter(country=obj).count()
    jobs_count.short_description = 'Jobs Available'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category Admin"""
    
    list_display = ('name', 'is_active', 'jobs_count')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)
    
    def jobs_count(self, obj):
        """Count jobs in this category"""
        return Job.objects.filter(category=obj).count()
    jobs_count.short_description = 'Jobs Available'


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    """Job Application Admin"""
    
    list_display = ('applicant', 'job', 'status', 'date_applied', 'date_updated')
    list_filter = ('status', 'date_applied', 'job__country')
    search_fields = ('applicant__email', 'applicant__full_name', 'job__title')
    readonly_fields = ('date_applied', 'date_updated', 'date_status_changed')
    date_hierarchy = 'date_applied'
    
    fieldsets = (
        ('Application Information', {
            'fields': ('job', 'applicant', 'status', 'cover_letter')
        }),
        ('Documents', {
            'fields': ('additional_documents',)
        }),
        ('Interview Details', {
            'fields': ('review_notes', 'interview_date', 'interview_notes')
        }),
        ('Offer Details', {
            'fields': ('offered_salary',)
        }),
        ('Timestamps', {
            'fields': ('date_applied', 'date_updated', 'date_status_changed'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['shortlist_applications', 'schedule_interviews', 'accept_applications', 
               'reject_applications']
    
    def shortlist_applications(self, request, queryset):
        count = queryset.update(status='shortlisted')
        self.message_user(request, f"{count} applications shortlisted.")
    shortlist_applications.short_description = "Shortlist selected applications"
    
    def schedule_interviews(self, request, queryset):
        count = queryset.update(status='interview_scheduled')
        self.message_user(request, f"{count} applications scheduled for interview.")
    schedule_interviews.short_description = "Schedule interviews for selected applications"
    
    def accept_applications(self, request, queryset):
        count = queryset.update(status='accepted')
        self.message_user(request, f"{count} applications accepted.")
    accept_applications.short_description = "Accept selected applications"
    
    def reject_applications(self, request, queryset):
        count = queryset.update(status='rejected')
        self.message_user(request, f"{count} applications rejected.")
    reject_applications.short_description = "Reject selected applications"


@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    """Payment Plan Admin"""
    
    list_display = ('name', 'plan_type', 'amount', 'currency', 'is_active')
    list_filter = ('plan_type', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('amount',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """User Profile Admin"""
    
    list_display = ('user', 'has_cv', 'has_photo', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'user__full_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Documents', {
            'fields': ('cv', 'national_id_document', 'passport_document', 'photo', 'cover_letter')
        }),
        ('Information', {
            'fields': ('education', 'work_experience', 'skills', 'languages', 'certifications')
        }),
        ('Additional', {
            'fields': ('bio', 'linkedin_url', 'website')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_cv(self, obj):
        return bool(obj.cv)
    has_cv.boolean = True
    has_cv.short_description = 'Has CV'
    
    def has_photo(self, obj):
        return bool(obj.photo)
    has_photo.boolean = True
    has_photo.short_description = 'Has Photo'


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    """System Setting Admin"""
    
    list_display = ('key', 'value_display', 'value_type', 'is_public', 'updated_at')
    list_filter = ('value_type', 'is_public')
    search_fields = ('key', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Setting', {
            'fields': ('key', 'value', 'value_type', 'description')
        }),
        ('Options', {
            'fields': ('is_public',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def value_display(self, obj):
        """Display value with truncation"""
        if len(obj.value) > 50:
            return obj.value[:50] + '...'
        return obj.value
    value_display.short_description = 'Value'


@admin.register(AdminActionLog)
class AdminActionLogAdmin(admin.ModelAdmin):
    """Admin Action Log Admin (Read-only)"""
    
    list_display = ('admin', 'action_type', 'model_name', 'object_repr', 'created_at')
    list_filter = ('action_type', 'model_name', 'created_at')
    search_fields = ('admin__email', 'admin__full_name', 'object_repr')
    readonly_fields = ('id', 'admin', 'action_type', 'model_name', 'object_id', 
                      'object_repr', 'changes', 'ip_address', 'user_agent', 'created_at')
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    """Admin Notification Admin"""
    
    list_display = ('title', 'priority', 'is_read', 'created_at')
    list_filter = ('priority', 'is_read', 'created_at')
    search_fields = ('title', 'message')
    readonly_fields = ('created_at', 'read_at')
    
    fieldsets = (
        ('Notification', {
            'fields': ('title', 'message', 'priority', 'link')
        }),
        ('Status', {
            'fields': ('is_read',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'read_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread', 'delete_selected']
    
    def mark_as_read(self, request, queryset):
        count = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f"{count} notifications marked as read.")
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        count = queryset.update(is_read=False, read_at=None)
        self.message_user(request, f"{count} notifications marked as unread.")
    mark_as_unread.short_description = "Mark selected notifications as unread"
    
    def delete_selected(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} notifications deleted.")
    delete_selected.short_description = "Delete selected notifications"


# ==============================================
# REGISTER ALL MODELS
# ==============================================

# Register the custom user admin
admin.site.register(User, CustomUserAdmin)

# Register all other models (already registered with decorators above)
# The following are registered with @admin.register:
# - Job
# - EmployerProfile
# - RecruitmentAgency
# - Payment
# - Country
# - Category
# - JobApplication
# - PaymentPlan
# - UserProfile
# - SystemSetting
# - AdminActionLog
# - AdminNotification

# Admin site customization
admin.site.site_header = 'Government Jobs Portal Administration'
admin.site.site_title = 'Gov Jobs Admin'
admin.site.index_title = 'Welcome to Government Jobs Portal Admin Panel'

# Customize admin templates
admin.site.enable_nav_sidebar = True