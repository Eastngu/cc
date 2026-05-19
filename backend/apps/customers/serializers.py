from rest_framework import serializers
from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'short_name', 'contact_person', 'phone',
            'address', 'payment_terms', 'default_billing_type',
            'remark', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CustomerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'short_name', 'contact_person', 'phone',
            'payment_terms', 'default_billing_type', 'is_active',
        ]
