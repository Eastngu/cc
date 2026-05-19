from django.contrib import admin
from .models import PlatingProcess, PricingRule


@admin.register(PlatingProcess)
class PlatingProcessAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'unit', 'base_price', 'is_active']
    list_filter = ['unit', 'is_active']
    search_fields = ['name', 'code']


@admin.register(PricingRule)
class PricingRuleAdmin(admin.ModelAdmin):
    list_display = ['plating_process', 'customer', 'unit_price', 'min_charge', 'effective_date']
    list_filter = ['plating_process', 'effective_date']
