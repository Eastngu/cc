from rest_framework import viewsets, status
from rest_framework.response import Response
from apps.users.permissions import IsBossOrFinance
from .filters import CustomerFilter
from .models import Customer
from .serializers import CustomerListSerializer, CustomerSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    filterset_class = CustomerFilter
    search_fields = ['name', 'short_name', 'contact_person', 'phone']
    ordering_fields = ['name', 'created_at', 'payment_terms']

    def get_serializer_class(self):
        if self.action == 'list':
            return CustomerListSerializer
        return CustomerSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsBossOrFinance()]
        return super().get_permissions()

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list' and 'is_active' not in self.request.query_params:
            qs = qs.filter(is_active=True)
        return qs

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=['is_active'])
        return Response(status=status.HTTP_204_NO_CONTENT)
