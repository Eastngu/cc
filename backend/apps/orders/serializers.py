from rest_framework import serializers
from .models import Order


class OrderListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.short_name', read_only=True)
    process_name = serializers.CharField(source='plating_process.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_no', 'customer', 'customer_name',
            'plating_process', 'process_name',
            'product_name', 'product_spec', 'quantity', 'unit',
            'unit_price', 'total_amount', 'status', 'status_display',
            'received_at', 'shipped_at', 'created_at',
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.short_name', read_only=True)
    process_name = serializers.CharField(source='plating_process.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.real_name', read_only=True, default='')

    class Meta:
        model = Order
        fields = [
            'id', 'order_no', 'customer', 'customer_name',
            'plating_process', 'process_name',
            'product_name', 'product_spec', 'quantity', 'unit',
            'unit_price', 'total_amount', 'status', 'status_display',
            'received_at', 'completed_at', 'shipped_at',
            'remark', 'created_by', 'created_by_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'order_no', 'total_amount', 'created_by', 'created_at', 'updated_at']


class OrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
