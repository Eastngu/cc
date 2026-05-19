import pytest
from apps.customers.models import Customer


@pytest.mark.django_db
class TestCustomerModel:
    def test_create_customer(self):
        customer = Customer.objects.create(
            name='深圳市ABC电子有限公司',
            short_name='ABC电子',
            contact_person='张三',
            phone='13900139000',
            address='深圳市宝安区XX路XX号',
            payment_terms=30,
            default_billing_type='area',
        )
        assert customer.name == '深圳市ABC电子有限公司'
        assert customer.short_name == 'ABC电子'
        assert customer.payment_terms == 30
        assert customer.default_billing_type == 'area'
        assert customer.is_active is True
        assert str(customer) == 'ABC电子'

    def test_soft_delete(self):
        customer = Customer.objects.create(
            name='测试公司',
            short_name='测试',
        )
        customer.is_active = False
        customer.save()
        assert Customer.objects.filter(is_active=True).count() == 0
        assert Customer.objects.count() == 1
