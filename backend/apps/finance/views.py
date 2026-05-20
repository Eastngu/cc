from rest_framework import viewsets
from apps.users.permissions import IsBossOrFinance
from .models import Receivable, Payable, Payment
from .serializers import ReceivableSerializer, PayableSerializer, PaymentSerializer


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
