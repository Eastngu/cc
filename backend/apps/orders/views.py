from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from apps.users.permissions import IsBossOrFinance
from .models import Order
from .serializers import OrderListSerializer, OrderDetailSerializer, OrderStatusSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related('customer', 'plating_process', 'created_by').all()
    search_fields = ['order_no', 'product_name', 'customer__name', 'customer__short_name']
    filterset_fields = ['customer', 'plating_process', 'status']
    ordering_fields = ['order_no', 'total_amount', 'created_at', 'status']

    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        if self.action == 'change_status':
            return OrderStatusSerializer
        return OrderDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['patch'], url_path='status')
    def change_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_status = serializer.validated_data['status']

        # Update date fields based on status
        now = timezone.now().date()
        if new_status == 'completed' and not order.completed_at:
            order.completed_at = now
        elif new_status == 'shipped' and not order.shipped_at:
            order.shipped_at = now

        order.status = new_status
        order.save()
        return Response(OrderDetailSerializer(order).data)
