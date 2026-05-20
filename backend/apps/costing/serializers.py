from rest_framework import serializers
from .models import OrderCost


class OrderCostSerializer(serializers.ModelSerializer):
    order_no = serializers.CharField(source='order.order_no', read_only=True)
    order_amount = serializers.DecimalField(
        source='order.total_amount', max_digits=12, decimal_places=2, read_only=True,
    )
    customer_name = serializers.CharField(source='order.customer.short_name', read_only=True)

    class Meta:
        model = OrderCost
        fields = [
            'id', 'order', 'order_no', 'order_amount', 'customer_name',
            'material_cost', 'electricity_cost', 'labor_cost', 'other_cost',
            'total_cost', 'profit', 'profit_rate', 'remark',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'total_cost', 'profit', 'profit_rate', 'created_at', 'updated_at']


class CostSummarySerializer(serializers.Serializer):
    """For the cost summary endpoint."""
    customer_id = serializers.IntegerField()
    customer_name = serializers.CharField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_cost = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_profit = serializers.DecimalField(max_digits=12, decimal_places=2)
    avg_profit_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    order_count = serializers.IntegerField()
