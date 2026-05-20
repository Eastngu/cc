from django.contrib import admin
from .models import OrderCost


@admin.register(OrderCost)
class OrderCostAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'material_cost', 'electricity_cost', 'labor_cost',
        'other_cost', 'total_cost', 'profit', 'profit_rate',
    ]
    list_filter = ['order__customer', 'order__plating_process']
    search_fields = ['order__order_no']
    readonly_fields = ['total_cost', 'profit', 'profit_rate']
