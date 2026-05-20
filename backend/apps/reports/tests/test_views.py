import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone

from apps.customers.models import Customer
from apps.processes.models import PlatingProcess
from apps.orders.models import Order
from apps.finance.models import Receivable, Payment
from apps.costing.models import OrderCost

User = get_user_model()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='staff1', password='pass123', role='finance', real_name='财务',
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


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
def shipped_order(db, customer, plating_process, user):
    today = timezone.now().date()
    return Order.objects.create(
        customer=customer,
        plating_process=plating_process,
        product_name='铝合金外壳',
        quantity=Decimal('200.00'),
        unit='dm²',
        unit_price=Decimal('5.0000'),
        total_amount=Decimal('1000.00'),
        shipped_at=today,
        created_by=user,
    )


@pytest.fixture
def order_cost(db, shipped_order):
    return OrderCost.objects.create(
        order=shipped_order,
        material_cost=Decimal('300.00'),
        electricity_cost=Decimal('100.00'),
        labor_cost=Decimal('150.00'),
        other_cost=Decimal('50.00'),
    )


@pytest.fixture
def receivable(db, customer):
    today = timezone.now().date()
    return Receivable.objects.create(
        customer=customer,
        year=today.year,
        month=today.month,
        total_amount=Decimal('1000.00'),
        received_amount=Decimal('400.00'),
        balance=Decimal('600.00'),
        due_date=today,
    )


@pytest.fixture
def pay_payment(db, user):
    today = timezone.now().date()
    return Payment.objects.create(
        type='pay',
        amount=Decimal('500.00'),
        payment_date=today,
        created_by=user,
    )


# ---------------------------------------------------------------------------
# Dashboard tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestDashboardView:
    def test_dashboard_returns_all_fields(self, auth_client):
        response = auth_client.get('/api/v1/reports/dashboard/')
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert 'monthly_revenue' in data
        assert 'monthly_expense' in data
        assert 'monthly_profit' in data
        assert 'receivable_balance' in data
        assert 'last_month_revenue' in data
        assert 'revenue_change_rate' in data

    def test_dashboard_no_data_returns_zeros(self, auth_client):
        response = auth_client.get('/api/v1/reports/dashboard/')
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert data['monthly_revenue'] == 0
        assert data['monthly_expense'] == 0
        assert data['monthly_profit'] == 0
        assert data['receivable_balance'] == 0
        assert data['revenue_change_rate'] == 0

    def test_dashboard_reflects_current_month_data(
        self, auth_client, shipped_order, order_cost, pay_payment, receivable
    ):
        response = auth_client.get('/api/v1/reports/dashboard/')
        assert response.status_code == status.HTTP_200_OK
        data = response.data
        # Revenue: shipped order total_amount
        assert Decimal(str(data['monthly_revenue'])) == Decimal('1000.00')
        # Expense: pay payment
        assert Decimal(str(data['monthly_expense'])) == Decimal('500.00')
        # Receivable balance: 600 (open/partial)
        assert Decimal(str(data['receivable_balance'])) == Decimal('600.00')

    def test_dashboard_unauthenticated_returns_401(self, api_client):
        response = api_client.get('/api/v1/reports/dashboard/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Revenue trend tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestRevenueTrendView:
    def test_revenue_trend_returns_6_months(self, auth_client):
        response = auth_client.get('/api/v1/reports/revenue-trend/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 6

    def test_revenue_trend_has_correct_fields(self, auth_client):
        response = auth_client.get('/api/v1/reports/revenue-trend/')
        assert response.status_code == status.HTTP_200_OK
        for item in response.data:
            assert 'month' in item
            assert 'revenue' in item
            assert 'cost' in item
            assert 'profit' in item

    def test_revenue_trend_month_format(self, auth_client):
        response = auth_client.get('/api/v1/reports/revenue-trend/')
        assert response.status_code == status.HTTP_200_OK
        for item in response.data:
            # Format should be YYYY-MM
            assert len(item['month']) == 7
            assert item['month'][4] == '-'

    def test_revenue_trend_unauthenticated_returns_401(self, api_client):
        response = api_client.get('/api/v1/reports/revenue-trend/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Customer analysis tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestCustomerAnalysisView:
    def test_customer_analysis_returns_list(self, auth_client, shipped_order, receivable):
        response = auth_client.get('/api/v1/reports/customer-analysis/')
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)

    def test_customer_analysis_has_correct_fields(self, auth_client, shipped_order, receivable):
        response = auth_client.get('/api/v1/reports/customer-analysis/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        item = response.data[0]
        assert 'customer_id' in item
        assert 'customer_name' in item
        assert 'total_receivable' in item
        assert 'total_received' in item
        assert 'collection_rate' in item
        assert 'outstanding_balance' in item
        assert 'total_profit' in item
        assert 'order_count' in item

    def test_customer_analysis_customer_name_uses_short_name(
        self, auth_client, shipped_order, receivable
    ):
        response = auth_client.get('/api/v1/reports/customer-analysis/')
        assert response.status_code == status.HTTP_200_OK
        names = [item['customer_name'] for item in response.data]
        assert 'ABC电子' in names

    def test_customer_analysis_empty_when_no_activity(self, auth_client):
        # No orders or receivables → result list is empty
        response = auth_client.get('/api/v1/reports/customer-analysis/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_customer_analysis_unauthenticated_returns_401(self, api_client):
        response = api_client.get('/api/v1/reports/customer-analysis/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ---------------------------------------------------------------------------
# Cost analysis tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestCostAnalysisView:
    def test_cost_analysis_returns_by_process(self, auth_client):
        response = auth_client.get('/api/v1/reports/cost-analysis/')
        assert response.status_code == status.HTTP_200_OK
        assert 'by_process' in response.data

    def test_cost_analysis_by_process_fields(self, auth_client, order_cost):
        response = auth_client.get('/api/v1/reports/cost-analysis/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['by_process']) >= 1
        item = response.data['by_process'][0]
        assert 'process_name' in item
        assert 'order_count' in item
        assert 'total_revenue' in item
        assert 'total_cost' in item
        assert 'total_profit' in item
        assert 'avg_profit_rate' in item

    def test_cost_analysis_empty_by_process_when_no_costs(self, auth_client, plating_process):
        # Active process exists but no cost records
        response = auth_client.get('/api/v1/reports/cost-analysis/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['by_process'] == []

    def test_cost_analysis_unauthenticated_returns_401(self, api_client):
        response = api_client.get('/api/v1/reports/cost-analysis/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
