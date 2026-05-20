import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from apps.customers.models import Customer
from apps.processes.models import PlatingProcess
from apps.orders.models import Order
from apps.costing.models import OrderCost

User = get_user_model()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

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


@pytest.fixture
def plating_process(db):
    return PlatingProcess.objects.create(
        name='镀锌',
        code='ZN001',
        unit='area',
        base_price=Decimal('5.00'),
    )


@pytest.fixture
def sample_order(db, customer, plating_process):
    return Order.objects.create(
        customer=customer,
        plating_process=plating_process,
        product_name='铝合金外壳',
        product_spec='100x50mm',
        quantity=Decimal('200.00'),
        unit='dm²',
        unit_price=Decimal('5.0000'),
        total_amount=Decimal('1000.00'),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestOrderCostCreation:
    def test_auto_calculates_total_cost(self, sample_order):
        cost = OrderCost.objects.create(
            order=sample_order,
            material_cost=Decimal('200.00'),
            electricity_cost=Decimal('100.00'),
            labor_cost=Decimal('150.00'),
            other_cost=Decimal('50.00'),
        )
        assert cost.total_cost == Decimal('500.00')

    def test_auto_calculates_profit(self, sample_order):
        # order total_amount = 1000.00, total_cost = 600.00 → profit = 400.00
        cost = OrderCost.objects.create(
            order=sample_order,
            material_cost=Decimal('300.00'),
            electricity_cost=Decimal('150.00'),
            labor_cost=Decimal('100.00'),
            other_cost=Decimal('50.00'),
        )
        assert cost.total_cost == Decimal('600.00')
        assert cost.profit == Decimal('400.00')

    def test_profit_rate_calculation(self, sample_order):
        # order=1000, total_cost=600, profit=400, rate=40%
        cost = OrderCost.objects.create(
            order=sample_order,
            material_cost=Decimal('300.00'),
            electricity_cost=Decimal('150.00'),
            labor_cost=Decimal('100.00'),
            other_cost=Decimal('50.00'),
        )
        assert cost.profit_rate == Decimal('40.00')

    def test_zero_order_amount_profit_rate_is_zero(self, customer, plating_process):
        order = Order.objects.create(
            customer=customer,
            plating_process=plating_process,
            product_name='零金额产品',
            quantity=Decimal('10.00'),
            unit='dm²',
            unit_price=Decimal('0.0000'),
            total_amount=Decimal('0.00'),
        )
        cost = OrderCost.objects.create(
            order=order,
            material_cost=Decimal('100.00'),
        )
        assert cost.profit_rate == Decimal('0')

    def test_str_representation(self, sample_order):
        cost = OrderCost.objects.create(order=sample_order)
        assert str(cost) == f'{sample_order.order_no} 成本'

    def test_defaults_are_zero(self, sample_order):
        cost = OrderCost.objects.create(order=sample_order)
        assert cost.material_cost == Decimal('0')
        assert cost.electricity_cost == Decimal('0')
        assert cost.labor_cost == Decimal('0')
        assert cost.other_cost == Decimal('0')
        assert cost.total_cost == Decimal('0')

    def test_update_recalculates(self, sample_order):
        cost = OrderCost.objects.create(
            order=sample_order,
            material_cost=Decimal('100.00'),
        )
        assert cost.total_cost == Decimal('100.00')

        cost.labor_cost = Decimal('200.00')
        cost.save()
        assert cost.total_cost == Decimal('300.00')
        assert cost.profit == Decimal('700.00')
