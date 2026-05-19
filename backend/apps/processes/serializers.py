from rest_framework import serializers
from .models import PlatingProcess, PricingRule


class PlatingProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatingProcess
        fields = ['id', 'name', 'code', 'unit', 'base_price', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PricingRuleSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.short_name', read_only=True, default='通用')
    process_name = serializers.CharField(source='plating_process.name', read_only=True)

    class Meta:
        model = PricingRule
        fields = ['id', 'customer', 'customer_name', 'plating_process', 'process_name', 'unit_price', 'min_charge', 'effective_date', 'remark', 'created_at']
        read_only_fields = ['id', 'created_at']
