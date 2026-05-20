import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.customers.models import Customer
from apps.processes.models import PlatingProcess
from apps.orders.models import Order
from apps.costing.models import OrderCost

User = get_user_model()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def boss_user(db):
    return User.objects.create_user(
        username='boss1', password='pass123', role='boss', real_name='老板',
    )


@pytest.fixture
def finance_user(db):
    return User.objects.create_user(
        username='finance1', password='pass123', role='finance', real_name='财务员',
    )


@pytest.fixture
def workshop_user(db):
    return User.objects.create_user(
        username='workshop1', password='pass123', role='workshop', real_name='车间主管',
    )


@pytest.fixture
def api_client():
    return APIClient()


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
def customer2(db):
    return Customer.objects.create(
        name='上海XYZ科技有限公司',
        short_name='XYZ科技',
        contact_person='李四',
        phone='13800138000',
        payment_terms=60,
        default_billing_type='weight',
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
def sample_order(db, customer, plating_process, finance_user):
    return Order.objects.create(
        customer=customer,
        plating_process=plating_process,
        product_name='铝合金外壳',
        product_spec='100x50mm',
        quantity=Decimal('200.00'),
        unit='dm²',
        unit_price=Decimal('5.0000'),
        total_amount=Decimal('1000.00'),
        created_by=finance_user,
    )


@pytest.fixture
def sample_order2(db, customer2, plating_process, finance_user):
    return Order.objects.create(
        customer=customer2,
        plating_process=plating_process,
        product_name='铜质零件',
        product_spec='M10',
        quantity=Decimal('100.00'),
        unit='dm²',
        unit_price=Decimal('8.0000'),
        total_amount=Decimal('800.00'),
        created_by=finance_user,
    )


@pytest.fixture
def sample_cost(db, sample_order):
    return OrderCost.objects.create(
        order=sample_order,
        material_cost=Decimal('300.00'),
        electricity_cost=Decimal('100.00'),
        labor_cost=Decimal('150.00'),
        other_cost=Decimal('50.00'),
    )


# ---------------------------------------------------------------------------
# CRUD tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestOrderCostCreate:
    def test_create_order_cost(self, api_client, finance_user, sample_order):
        api_client.force_authenticate(user=finance_user)
        data = {
            'order': sample_order.id,
            'material_cost': '300.00',
            'electricity_cost': '100.00',
            'labor_cost': '150.00',
            'other_cost': '50.00',
        }
        response = api_client.post('/api/v1/costing/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['total_cost'] == '600.00'
        assert response.data['profit'] == '400.00'
        assert response.data['profit_rate'] == '40.00'

    def test_create_returns_computed_fields(self, api_client, finance_user, sample_order):
        api_client.force_authenticate(user=finance_user)
        data = {
            'order': sample_order.id,
            'material_cost': '200.00',
            'electricity_cost': '100.00',
            'labor_cost': '100.00',
            'other_cost': '0.00',
        }
        response = api_client.post('/api/v1/costing/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['order_no'] == sample_order.order_no
        assert response.data['customer_name'] == 'ABC电子'
        assert response.data['order_amount'] == '1000.00'
        assert response.data['total_cost'] == '400.00'
        assert response.data['profit'] == '600.00'

    def test_workshop_user_gets_403(self, api_client, workshop_user, sample_order):
        api_client.force_authenticate(user=workshop_user)
        data = {
            'order': sample_order.id,
            'material_cost': '100.00',
        }
        response = api_client.post('/api/v1/costing/', data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_gets_401(self, api_client, sample_order):
        data = {'order': sample_order.id, 'material_cost': '100.00'}
        response = api_client.post('/api/v1/costing/', data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_boss_can_create(self, api_client, boss_user, sample_order):
        api_client.force_authenticate(user=boss_user)
        data = {'order': sample_order.id, 'material_cost': '200.00'}
        response = api_client.post('/api/v1/costing/', data)
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestOrderCostUpdate:
    def test_update_recalculates_costs(self, api_client, finance_user, sample_cost):
        api_client.force_authenticate(user=finance_user)
        response = api_client.patch(
            f'/api/v1/costing/{sample_cost.id}/',
            {'labor_cost': '250.00'},
        )
        assert response.status_code == status.HTTP_200_OK
        # material=300, electricity=100, labor=250, other=50 → total=700
        assert response.data['total_cost'] == '700.00'
        assert response.data['profit'] == '300.00'
        # profit_rate = 300/1000 * 100 = 30%
        assert response.data['profit_rate'] == '30.00'

    def test_read_only_fields_ignored_in_update(self, api_client, finance_user, sample_cost):
        api_client.force_authenticate(user=finance_user)
        # Attempt to set total_cost directly — should be ignored, recalculated
        response = api_client.patch(
            f'/api/v1/costing/{sample_cost.id}/',
            {'total_cost': '9999.00', 'material_cost': '100.00'},
        )
        assert response.status_code == status.HTTP_200_OK
        # material=100, electricity=100, labor=150, other=50 → total=400, not 9999
        assert response.data['total_cost'] == '400.00'


@pytest.mark.django_db
class TestOrderCostList:
    def test_list_costs(self, api_client, finance_user, sample_cost):
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/costing/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_filter_by_customer(self, api_client, finance_user, sample_order, sample_order2,
                                sample_cost, customer):
        # Create a cost for order2 too
        OrderCost.objects.create(
            order=sample_order2,
            material_cost=Decimal('200.00'),
        )
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/costing/', {'order__customer': customer.id})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['customer_name'] == 'ABC电子'

    def test_workshop_gets_403_on_list(self, api_client, workshop_user):
        api_client.force_authenticate(user=workshop_user)
        response = api_client.get('/api/v1/costing/')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCostSummary:
    def test_summary_groups_by_customer(self, api_client, finance_user,
                                        sample_order, sample_order2):
        # Create costs for two different customers
        OrderCost.objects.create(
            order=sample_order,
            material_cost=Decimal('300.00'),
            electricity_cost=Decimal('100.00'),
            labor_cost=Decimal('150.00'),
            other_cost=Decimal('50.00'),
        )
        OrderCost.objects.create(
            order=sample_order2,
            material_cost=Decimal('200.00'),
            electricity_cost=Decimal('80.00'),
            labor_cost=Decimal('100.00'),
            other_cost=Decimal('20.00'),
        )
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/costing/summary/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        # Verify summary fields are present
        first = response.data[0]
        assert 'customer_id' in first
        assert 'customer_name' in first
        assert 'total_revenue' in first
        assert 'total_cost' in first
        assert 'total_profit' in first
        assert 'avg_profit_rate' in first
        assert 'order_count' in first

    def test_summary_correct_aggregates(self, api_client, finance_user, sample_order):
        # order total_amount=1000, material=600 → total_cost=600, profit=400, rate=40%
        OrderCost.objects.create(
            order=sample_order,
            material_cost=Decimal('600.00'),
        )
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/costing/summary/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        row = response.data[0]
        assert row['customer_name'] == 'ABC电子'
        assert row['order_count'] == 1
        assert Decimal(row['total_revenue']) == Decimal('1000.00')
        assert Decimal(row['total_cost']) == Decimal('600.00')
        assert Decimal(row['total_profit']) == Decimal('400.00')

    def test_summary_filter_by_year(self, api_client, finance_user, sample_order):
        OrderCost.objects.create(order=sample_order, material_cost=Decimal('400.00'))
        api_client.force_authenticate(user=finance_user)
        # Filter for current year — should return 1 result
        response = api_client.get('/api/v1/costing/summary/', {'year': '2026'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_summary_filter_by_wrong_year_returns_empty(self, api_client, finance_user, sample_order):
        OrderCost.objects.create(order=sample_order, material_cost=Decimal('400.00'))
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/costing/summary/', {'year': '2000'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_summary_workshop_gets_403(self, api_client, workshop_user):
        api_client.force_authenticate(user=workshop_user)
        response = api_client.get('/api/v1/costing/summary/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
