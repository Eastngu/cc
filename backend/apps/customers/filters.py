import django_filters
from .models import Customer


class CustomerFilter(django_filters.FilterSet):
    billing_type = django_filters.ChoiceFilter(
        field_name='default_billing_type',
        choices=Customer.BILLING_TYPE_CHOICES,
    )
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Customer
        fields = ['default_billing_type', 'is_active']
