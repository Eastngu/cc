from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum
from apps.users.permissions import IsBossOrFinance
from .models import Receivable, Payable, Payment, MonthlyStatement
from .serializers import (
    ReceivableSerializer, PayableSerializer, PaymentSerializer,
    MonthlyStatementListSerializer, MonthlyStatementDetailSerializer,
)


class ReceivableViewSet(viewsets.ModelViewSet):
    queryset = Receivable.objects.select_related('customer').all()
    serializer_class = ReceivableSerializer
    permission_classes = [IsBossOrFinance]
    filterset_fields = ['customer', 'status', 'year', 'month']
    search_fields = ['receivable_no', 'customer__name', 'customer__short_name']
    ordering_fields = ['total_amount', 'balance', 'due_date', 'created_at']


class PayableViewSet(viewsets.ModelViewSet):
    queryset = Payable.objects.all()
    serializer_class = PayableSerializer
    permission_classes = [IsBossOrFinance]
    filterset_fields = ['status', 'category']
    search_fields = ['payable_no', 'supplier_name']
    ordering_fields = ['total_amount', 'balance', 'due_date']


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('customer', 'receivable', 'payable').all()
    serializer_class = PaymentSerializer
    permission_classes = [IsBossOrFinance]
    filterset_fields = ['type', 'customer', 'payment_method']
    search_fields = ['payment_no']
    ordering_fields = ['amount', 'payment_date', 'created_at']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class MonthlyStatementViewSet(viewsets.ModelViewSet):
    queryset = MonthlyStatement.objects.select_related('customer', 'confirmed_by').all()
    permission_classes = [IsBossOrFinance]
    filterset_fields = ['customer', 'status', 'year', 'month']
    search_fields = ['statement_no', 'customer__name', 'customer__short_name']

    def get_serializer_class(self):
        if self.action == 'list':
            return MonthlyStatementListSerializer
        return MonthlyStatementDetailSerializer

    @action(detail=False, methods=['post'], url_path='generate')
    def generate(self, request):
        """Generate statement for a customer+month by pulling all shipped orders."""
        customer_id = request.data.get('customer')
        year = request.data.get('year')
        month = request.data.get('month')

        if not all([customer_id, year, month]):
            return Response({'detail': '请提供客户、年份和月份'}, status=400)

        year, month = int(year), int(month)

        if MonthlyStatement.objects.filter(customer_id=customer_id, year=year, month=month).exists():
            return Response({'detail': '该客户本月对账单已存在'}, status=400)

        from apps.orders.models import Order
        orders = Order.objects.filter(
            customer_id=customer_id,
            status='shipped',
            shipped_at__year=year,
            shipped_at__month=month,
        )

        total = orders.aggregate(total=Sum('total_amount'))['total'] or 0

        statement = MonthlyStatement.objects.create(
            customer_id=customer_id,
            year=year,
            month=month,
            total_amount=total,
        )
        statement.orders.set(orders)

        serializer = MonthlyStatementDetailSerializer(statement)
        return Response(serializer.data, status=201)

    @action(detail=True, methods=['patch'], url_path='confirm')
    def confirm(self, request, pk=None):
        """Confirm a statement and auto-create a receivable."""
        statement = self.get_object()
        if statement.status != 'draft':
            return Response({'detail': '只有草稿状态可以确认'}, status=400)

        statement.status = 'confirmed'
        statement.confirmed_by = request.user
        statement.confirmed_at = timezone.now()
        statement.save()

        customer = statement.customer
        import datetime
        due_date = timezone.now().date() + datetime.timedelta(days=customer.payment_terms)

        receivable, created = Receivable.objects.get_or_create(
            customer=customer,
            year=statement.year,
            month=statement.month,
            defaults={
                'total_amount': statement.final_amount,
                'due_date': due_date,
            }
        )
        if not created:
            receivable.total_amount = statement.final_amount
            receivable.save()

        serializer = MonthlyStatementDetailSerializer(statement)
        return Response(serializer.data)
