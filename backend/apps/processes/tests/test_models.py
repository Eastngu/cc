import pytest
from decimal import Decimal
from apps.processes.models import PlatingProcess, PricingRule
from apps.customers.models import Customer


@pytest.fixture
def plating_process(db):
    return PlatingProcess.objects.create(
        name='镀锌',
        code='ZN001',
        unit='area',
        base_price=Decimal('5.00'),
        description='普通镀锌工艺',
        is_active=True,
    )


@pytest.fixture
def customer(db):
    return Customer.objects.create(
        name='深圳市ABC电子有限公司',
        short_name='ABC电子',
        contact_person='张三',
        phone='13900139000',
        payment_terms=30,
        default_billing_type='area',
    )


@pytest.mark.django_db
class TestPlatingProcessModel:
    def test_create_plating_process(self, plating_process):
        assert plating_process.id is not None
        assert plating_process.name == '镀锌'
        assert plating_process.code == 'ZN001'
        assert plating_process.unit == 'area'
        assert plating_process.base_price == Decimal('5.00')
        assert plating_process.is_active is True

    def test_str_representation(self, plating_process):
        assert str(plating_process) == '镀锌(ZN001)'

    def test_code_unique_constraint(self, plating_process):
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            PlatingProcess.objects.create(
                name='镀锌2',
                code='ZN001',  # duplicate code
                unit='area',
                base_price=Decimal('6.00'),
            )

    def test_default_values(self, db):
        process = PlatingProcess.objects.create(name='镀铬', code='CR001')
        assert process.unit == 'area'
        assert process.base_price == Decimal('0')
        assert process.is_active is True
        assert process.description == ''

    def test_ordering_by_code(self, db):
        PlatingProcess.objects.create(name='镀铜', code='CU001')
        PlatingProcess.objects.create(name='镀锌', code='ZN001')
        PlatingProcess.objects.create(name='镀铬', code='CR001')
        codes = list(PlatingProcess.objects.values_list('code', flat=True))
        assert codes == ['CR001', 'CU001', 'ZN001']


@pytest.mark.django_db
class TestPricingRuleModel:
    def test_create_pricing_rule_with_customer(self, plating_process, customer):
        rule = PricingRule.objects.create(
            customer=customer,
            plating_process=plating_process,
            unit_price=Decimal('4.5000'),
            min_charge=Decimal('50.00'),
            effective_date='2024-01-01',
        )
        assert rule.id is not None
        assert rule.customer == customer
        assert rule.plating_process == plating_process
        assert rule.unit_price == Decimal('4.5000')
        assert rule.min_charge == Decimal('50.00')

    def test_create_generic_pricing_rule(self, plating_process):
        rule = PricingRule.objects.create(
            customer=None,
            plating_process=plating_process,
            unit_price=Decimal('5.0000'),
            effective_date='2024-01-01',
        )
        assert rule.customer is None

    def test_str_with_customer(self, plating_process, customer):
        rule = PricingRule.objects.create(
            customer=customer,
            plating_process=plating_process,
            unit_price=Decimal('4.5000'),
            effective_date='2024-01-01',
        )
        assert 'ABC电子' in str(rule)
        assert '镀锌' in str(rule)

    def test_str_without_customer(self, plating_process):
        rule = PricingRule.objects.create(
            customer=None,
            plating_process=plating_process,
            unit_price=Decimal('5.0000'),
            effective_date='2024-01-01',
        )
        assert '通用' in str(rule)

    def test_cascade_delete_process(self, plating_process, customer):
        PricingRule.objects.create(
            customer=customer,
            plating_process=plating_process,
            unit_price=Decimal('4.5000'),
            effective_date='2024-01-01',
        )
        assert PricingRule.objects.count() == 1
        plating_process.delete()
        assert PricingRule.objects.count() == 0

    def test_default_min_charge(self, plating_process):
        rule = PricingRule.objects.create(
            plating_process=plating_process,
            unit_price=Decimal('5.0000'),
            effective_date='2024-01-01',
        )
        assert rule.min_charge == Decimal('0')
