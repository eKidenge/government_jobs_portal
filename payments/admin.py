from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import (
    PaymentPlan,
    Payment,
    PaymentTransaction,
    UserPaymentAccess,
    PaymentWebhook,
    Invoice,
    PaymentSettings,
)


@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'plan_type', 'amount', 'currency', 'is_active', 'popular', 'sort_order')
    list_filter = ('is_active', 'plan_type', 'currency')
    search_fields = ('name', 'description')
    ordering = ('sort_order', 'amount')
    fieldsets = (
        (None, {
            'fields': ('name', 'plan_type', 'amount', 'currency', 'description')
        }),
        ('Features & Settings', {
            'fields': ('features', 'duration_days', 'is_active', 'popular', 'recommended', 'sort_order')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'transaction_reference', 'user', 'amount', 'currency',
        'payment_method', 'status', 'payment_date', 'mpesa_receipt_number'
    )
    list_filter = ('status', 'payment_method', 'payment_date')
    search_fields = ('transaction_reference', 'user__email', 'user__username', 'mpesa_receipt_number')
    ordering = ('-payment_date',)
    readonly_fields = ('transaction_reference', 'payment_date', 'completed_date', 'created_at', 'updated_at')
    fields = (
        'user', 'plan', 'amount', 'currency', 'payment_method',
        'transaction_reference', 'mpesa_receipt_number', 'checkout_request_id',
        'status', 'payment_date', 'completed_date',
        'metadata'
    )
    actions = ['mark_completed', 'mark_failed', 'mark_refunded']

    def mark_completed(self, request, queryset):
        updated = queryset.update(status='completed', completed_date=timezone.now())
        self.message_user(request, f'{updated} payments marked as completed.')
    mark_completed.short_description = "Mark selected payments as Completed"

    def mark_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} payments marked as failed.')
    mark_failed.short_description = "Mark selected payments as Failed"

    def mark_refunded(self, request, queryset):
        updated = queryset.update(status='refunded')
        self.message_user(request, f'{updated} payments marked as refunded.')
    mark_refunded.short_description = "Mark selected payments as Refunded"


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('payment', 'transaction_type', 'status', 'created_at')
    list_filter = ('transaction_type', 'status')
    search_fields = ('payment__transaction_reference',)
    readonly_fields = ('created_at',)
    fields = (
        'payment', 'transaction_type', 'status',
        'request_data', 'response_data', 'error_message',
        'ip_address', 'user_agent'
    )


@admin.register(UserPaymentAccess)
class UserPaymentAccessAdmin(admin.ModelAdmin):
    list_display = ('user', 'has_access', 'access_start_date', 'access_end_date', 'applications_used', 'applications_limit')
    list_filter = ('has_access',)
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    fields = (
        'user', 'payment', 'has_access', 'access_start_date', 'access_end_date',
        'applications_used', 'applications_limit', 'metadata'
    )


@admin.register(PaymentWebhook)
class PaymentWebhookAdmin(admin.ModelAdmin):
    list_display = ('webhook_type', 'payment', 'processed', 'created_at', 'processed_at')
    list_filter = ('webhook_type', 'processed')
    search_fields = ('payment__transaction_reference',)
    readonly_fields = ('created_at',)
    fields = ('webhook_type', 'payment', 'payload', 'headers', 'processed', 'processing_error', 'ip_address')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'user', 'total_amount', 'status', 'issue_date', 'due_date')
    list_filter = ('status',)
    search_fields = ('invoice_number', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    fields = (
        'invoice_number', 'payment', 'user', 'amount', 'tax', 'total_amount',
        'issue_date', 'due_date', 'paid_date', 'status', 'items', 'notes'
    )


@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    list_display = ('key', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('key', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fields = ('key', 'value', 'description', 'is_active')