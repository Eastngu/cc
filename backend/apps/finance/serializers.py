from rest_framework import serializers
from .models import Receivable, Payable, Payment, MonthlyStatement


# Inline order serializer to avoid circular import
class _OrderSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    order_no = serializers.CharField(read_only=True)
    customer = serializers.IntegerField(source='customer_id', read_only=True)
    customer_name = serializers.CharField(source='customer.short_name', read_only=True)
    plating_process = serializers.IntegerField(source='plating_process_id', read_only=True)
    process_name = serializers.CharField(source='plating_process.name', read_only=True)
    product_name = serializers.CharField(read_only=True)
    product_spec = serializers.CharField(read_only=True)
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    unit = serializers.CharField(read_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    status = serializers.CharField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    received_at = serializers.DateField(read_only=True)
    shipped_at = serializers.DateField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


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


class MonthlyStatementListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.short_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    order_count = serializers.IntegerField(source='orders.count', read_only=True)

    class Meta:
        model = MonthlyStatement
        fields = ['id', 'statement_no', 'customer', 'customer_name', 'year', 'month',
                  'total_amount', 'adjustment', 'final_amount', 'status', 'status_display',
                  'order_count', 'created_at']


class MonthlyStatementDetailSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.short_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    confirmed_by_name = serializers.CharField(source='confirmed_by.real_name', read_only=True, default='')
    orders = _OrderSerializer(many=True, read_only=True)

    class Meta:
        model = MonthlyStatement
        fields = ['id', 'statement_no', 'customer', 'customer_name', 'year', 'month',
                  'total_amount', 'adjustment', 'final_amount', 'status', 'status_display',
                  'confirmed_by', 'confirmed_by_name', 'confirmed_at', 'orders', 'created_at', 'updated_at']
        read_only_fields = ['id', 'statement_no', 'total_amount', 'final_amount',
                            'confirmed_by', 'confirmed_at', 'created_at', 'updated_at']
