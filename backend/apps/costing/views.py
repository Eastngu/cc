from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Avg, Count, F

from apps.users.permissions import IsBossOrFinance
from .models import OrderCost
from .serializers import OrderCostSerializer, CostSummarySerializer


class OrderCostViewSet(viewsets.ModelViewSet):
    queryset = OrderCost.objects.select_related('order', 'order__customer').all()
    serializer_class = OrderCostSerializer
    permission_classes = [IsBossOrFinance]
    filterset_fields = ['order__customer', 'order__plating_process']
    search_fields = ['order__order_no', 'order__product_name']
    ordering_fields = ['total_cost', 'profit', 'profit_rate', 'created_at']

    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """Cost summary grouped by customer, optionally filtered by year/month."""
        qs = OrderCost.objects.select_related('order__customer')

        year = request.query_params.get('year')
        month = request.query_params.get('month')
        if year:
            qs = qs.filter(order__created_at__year=int(year))
        if month:
            qs = qs.filter(order__created_at__month=int(month))

        summary = qs.values(
            customer_id=F('order__customer__id'),
            customer_name=F('order__customer__short_name'),
        ).annotate(
            total_revenue=Sum('order__total_amount'),
            total_cost=Sum('total_cost'),
            total_profit=Sum('profit'),
            avg_profit_rate=Avg('profit_rate'),
            order_count=Count('id'),
        ).order_by('-total_profit')

        serializer = CostSummarySerializer(summary, many=True)
        return Response(serializer.data)
