import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from apps.customers.models import Customer
from apps.processes.models import PlatingProcess
from apps.orders.models import Order

User = get_user_model()


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
        unit_price=Decimal('4.5000'),
        total_amount=Decimal('900.00'),
    )


@pytest.mark.django_db
class TestOrderCreation:
    def test_auto_generated_order_no(self, customer, plating_process):
        order = Order.objects.create(
            customer=customer,
            plating_process=plating_process,
            product_name='测试产品',
            quantity=Decimal('100.00'),
            unit='dm²',
            unit_price=Decimal('5.0000'),
            total_amount=Decimal('500.00'),
        )
        assert order.order_no.startswith('DD')
        assert len(order.order_no) == 11  # DD + YYYYMM (6) + 3 digits = 11

    def test_sequential_order_nos(self, customer, plating_process):
        order1 = Order.objects.create(
            customer=customer,
            plating_process=plating_process,
            product_name='产品1',
            quantity=Decimal('100.00'),
            unit='dm²',
            unit_price=Decimal('5.0000'),
            total_amount=Decimal('500.00'),
        )
        order2 = Order.objects.create(
            customer=customer,
            plating_process=plating_process,
            product_name='产品2',
            quantity=Decimal('50.00'),
            unit='dm²',
            unit_price=Decimal('5.0000'),
            total_amount=Decimal('250.00'),
        )
        num1 = int(order1.order_no[-3:])
        num2 = int(order2.order_no[-3:])
        assert num2 == num1 + 1

    def test_explicit_order_no_not_overwritten(self, customer, plating_process):
        order = Order.objects.create(
            order_no='DD202601999',
            customer=customer,
            plating_process=plating_process,
            product_name='手动编号产品',
            quantity=Decimal('10.00'),
            unit='件',
            unit_price=Decimal('2.0000'),
            total_amount=Decimal('20.00'),
        )
        assert order.order_no == 'DD202601999'


@pytest.mark.django_db
class TestOrderTotalAmount:
    def test_total_amount_auto_calculated(self, customer, plating_process):
        order = Order(
            customer=customer,
            plating_process=plating_process,
            product_name='自动计算金额',
            quantity=Decimal('100.00'),
            unit='dm²',
            unit_price=Decimal('4.5000'),
        )
        # total_amount is not set yet, save should calculate it
        order.total_amount = None
        order.save()
        assert order.total_amount == Decimal('450.00')

    def test_explicit_total_amount_not_overwritten(self, customer, plating_process):
        order = Order.objects.create(
            customer=customer,
            plating_process=plating_process,
            product_name='手动金额产品',
            quantity=Decimal('100.00'),
            unit='dm²',
            unit_price=Decimal('4.5000'),
            total_amount=Decimal('999.00'),
        )
        assert order.total_amount == Decimal('999.00')


@pytest.mark.django_db
class TestOrderStr:
    def test_str_representation(self, sample_order):
        expected = f'{sample_order.order_no} - ABC电子'
        assert str(sample_order) == expected

    def test_default_status_is_pending(self, sample_order):
        assert sample_order.status == 'pending'
