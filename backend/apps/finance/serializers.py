from rest_framework import serializers
from .models import Receivable, Payable, Payment


class ReceivableSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.short_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Receivable
        fields = ['id', 'receivable_no', 'customer', 'customer_name', 'year', 'month',
                  'total_amount', 'received_amount', 'balance', 'status', 'status_display',
                  'due_date', 'created_at']
        read_only_fields = ['id', 'receivable_no', 'received_amount', 'balance', 'status', 'created_at']


class PayableSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)

    class Meta:
        model = Payable
        fields = ['id', 'payable_no', 'supplier_name', 'category', 'category_display',
                  'total_amount', 'paid_amount', 'balance', 'status', 'status_display',
                  'due_date', 'remark', 'created_at']
        read_only_fields = ['id', 'payable_no', 'paid_amount', 'balance', 'status', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    customer_name = serializers.CharField(source='customer.short_name', read_only=True, default='')

    class Meta:
        model = Payment
        fields = ['id', 'payment_no', 'type', 'type_display', 'customer', 'customer_name',
                  'receivable', 'payable', 'amount', 'payment_method', 'method_display',
                  'payment_date', 'remark', 'created_by', 'created_at']
        read_only_fields = ['id', 'payment_no', 'created_by', 'created_at']
