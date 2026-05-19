from rest_framework import viewsets
from apps.users.permissions import IsBossOrFinance
from .models import PlatingProcess, PricingRule
from .serializers import PlatingProcessSerializer, PricingRuleSerializer


class PlatingProcessViewSet(viewsets.ModelViewSet):
    queryset = PlatingProcess.objects.all()
    serializer_class = PlatingProcessSerializer
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'code', 'base_price']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsBossOrFinance()]
        return super().get_permissions()

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list' and 'is_active' not in self.request.query_params:
            qs = qs.filter(is_active=True)
        return qs


class PricingRuleViewSet(viewsets.ModelViewSet):
    queryset = PricingRule.objects.select_related('customer', 'plating_process').all()
    serializer_class = PricingRuleSerializer
    filterset_fields = ['customer', 'plating_process']
    ordering_fields = ['effective_date', 'unit_price']

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsBossOrFinance()]
        return super().get_permissions()
