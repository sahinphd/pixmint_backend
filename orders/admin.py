from django.contrib import admin
from .models import OrderHistory

@admin.register(OrderHistory)
class OrderHistoryAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = (
        'order_id',
        'user_id',
        'order_time',
        'order_amount',
        'order_currency',
        'pay_currency',
        'order_status',
    )

    # Fields to filter by in list view sidebar
    list_filter = ('order_status', 'order_currency', 'pay_currency', 'order_time')

    # Fields that can be searched
    search_fields = ('order_id', 'user_id', 'payment_id', 'payment_address')

    # Enable ordering by order_time descending by default
    ordering = ('-order_time',)

    # Fields editable in the change view form
    fields = (
        'user_id',
        'order_id',
        'payment_id',
        'order_time',
        'order_amount',
        'order_currency',
        'pay_currency',
        'order_status',
        'order_log',
        'payment_address',
        'api_log',
    )

    # Mark order_id and order_time as read-only in the form, since you generate order_id on save
    readonly_fields = ('order_id', 'order_time')

    # Optional: Add save hooks if you want to customize behavior on save
    # def save_model(self, request, obj, form, change):
    #     # custom save logic if needed
    #     super().save_model(request, obj, form, change)
