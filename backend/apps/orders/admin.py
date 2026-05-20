from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_no', 'customer', 'plating_process', 'product_name', 'quantity', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'plating_process', 'customer']
    search_fields = ['order_no', 'product_name']
    readonly_fields = ['order_no', 'total_amount', 'created_by']
