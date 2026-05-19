from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name', 'contact_person', 'phone', 'payment_terms', 'is_active']
    list_filter = ['is_active', 'default_billing_type', 'payment_terms']
    search_fields = ['name', 'short_name', 'contact_person']
