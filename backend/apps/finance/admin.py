from django.contrib import admin
from .models import Receivable, Payable, Payment


@admin.register(Receivable)
class ReceivableAdmin(admin.ModelAdmin):
    list_display = ['receivable_no', 'customer', 'year', 'month', 'total_amount', 'received_amount', 'balance', 'status']
    list_filter = ['status', 'year', 'month']


@admin.register(Payable)
class PayableAdmin(admin.ModelAdmin):
    list_display = ['payable_no', 'supplier_name', 'category', 'total_amount', 'paid_amount', 'balance', 'status']
    list_filter = ['status', 'category']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_no', 'type', 'customer', 'amount', 'payment_method', 'payment_date']
    list_filter = ['type', 'payment_method']
