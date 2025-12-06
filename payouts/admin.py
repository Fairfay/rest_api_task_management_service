from django.contrib import admin

from payouts.models import PayoutRequest


class PayoutRequestAdmin(admin.ModelAdmin):
    """Настройка отображения заявок на выплату в Django Admin."""

    list_display = (
        'id',
        'payment_sum',
        'currency',
        'status',
        'created_at',
        'updated_at',
    )
    list_filter = (
        'status',
        'currency',
        'created_at',
    )
    search_fields = (
        'id',
        'recipients_details',
        'comment',
    )
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status',)
    fieldsets = (
        (None, {
            'fields': (
                'payment_sum',
                'currency',
                'recipients_details',
                'status',
                'comment',
            )
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


admin.site.register(PayoutRequest, PayoutRequestAdmin)
