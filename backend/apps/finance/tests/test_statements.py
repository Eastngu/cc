import pytest
from decimal import Decimal
from datetime import date
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from apps.customers.models import Customer
from apps.processes.models import PlatingProcess
from apps.orders.models import Order
from apps.finance.models import MonthlyStatement, Receivable

User = get_user_model()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def finance_user(db):
    return User.objects.create_user(
        username='finance_st', password='pass123', role='finance', real_name='财务员',
    )


@pytest.fixture
def boss_user(db):
    return User.objects.create_user(
        username='boss_st', password='pass123', role='boss', real_name='老板',
    )


@pytest.fixture
def workshop_user(db):
    return User.objects.create_user(
        username='workshop_st', password='pass123', role='workshop', real_name='车间主管',
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


@pytest.fixture
def customer2(db):
    return Customer.objects.create(
        name='广州市XYZ机械有限公司',
        short_name='XYZ机械',
        payment_terms=60,
        default_billing_type='weight',
    )


@pytest.fixture
def plating_process(db):
    return PlatingProcess.objects.create(
        name='镀锌', code='ZN_ST', unit='area', base_price=Decimal('5.00'),
    )


def make_order(customer, plating_process, amount, shipped_year=None, shipped_month=None,
               status='shipped'):
    """Helper to create an order, optionally marking it as shipped in a given year/month."""
    order = Order.objects.create(
        customer=customer,
        plating_process=plating_process,
        product_name='测试产品',
        quantity=Decimal('100.00'),
        unit='dm²',
        unit_price=Decimal(str(amount)) / Decimal('100'),
        total_amount=Decimal(str(amount)),
        status=status,
    )
    if shipped_year and shipped_month:
        order.shipped_at = date(shipped_year, shipped_month, 15)
        order.save()
    return order


# ---------------------------------------------------------------------------
# Generate statement
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestGenerateStatement:
    def test_generate_creates_statement_with_correct_total(
        self, api_client, finance_user, customer, plating_process
    ):
        """Generate pulls all shipped orders for customer+month and sums total_amount."""
        make_order(customer, plating_process, '1000.00', 2025, 6)
        make_order(customer, plating_process, '2000.00', 2025, 6)

        api_client.force_authenticate(user=finance_user)
        response = api_client.post('/api/v1/statements/generate/', {
            'customer': customer.id,
            'year': 2025,
            'month': 6,
        })

        assert response.status_code == status.HTTP_201_CREATED
        data = response.data
        assert data['statement_no'].startswith('ST')
        assert Decimal(data['total_amount']) == Decimal('3000.00')
        assert Decimal(data['final_amount']) == Decimal('3000.00')
        assert data['status'] == 'draft'
        assert len(data['orders']) == 2

    def test_generate_only_includes_shipped_orders_for_customer_month(
        self, api_client, finance_user, customer, customer2, plating_process
    ):
        """Orders for other customers, other months, or non-shipped status are excluded."""
        # correct order
        make_order(customer, plating_process, '500.00', 2025, 5)
        # wrong month
        make_order(customer, plating_process, '800.00', 2025, 4)
        # wrong customer
        make_order(customer2, plating_process, '700.00', 2025, 5)
        # not shipped
        make_order(customer, plating_process, '300.00', 2025, 5, status='completed')

        api_client.force_authenticate(user=finance_user)
        response = api_client.post('/api/v1/statements/generate/', {
            'customer': customer.id,
            'year': 2025,
            'month': 5,
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert Decimal(response.data['total_amount']) == Decimal('500.00')
        assert len(response.data['orders']) == 1

    def test_generate_duplicate_returns_error(
        self, api_client, finance_user, customer, plating_process
    ):
        """Generating a statement that already exists returns 400."""
        MonthlyStatement.objects.create(
            customer=customer, year=2025, month=7, total_amount=Decimal('0'),
        )

        api_client.force_authenticate(user=finance_user)
        response = api_client.post('/api/v1/statements/generate/', {
            'customer': customer.id,
            'year': 2025,
            'month': 7,
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert '已存在' in response.data['detail']

    def test_generate_missing_params_returns_error(self, api_client, finance_user):
        """Missing customer/year/month returns 400."""
        api_client.force_authenticate(user=finance_user)
        response = api_client.post('/api/v1/statements/generate/', {'year': 2025})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_generate_zero_total_when_no_shipped_orders(
        self, api_client, finance_user, customer
    ):
        """Statement is still created with total_amount=0 when there are no matching orders."""
        api_client.force_authenticate(user=finance_user)
        response = api_client.post('/api/v1/statements/generate/', {
            'customer': customer.id,
            'year': 2024,
            'month': 12,
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert Decimal(response.data['total_amount']) == Decimal('0')
        assert response.data['orders'] == []


# ---------------------------------------------------------------------------
# Confirm statement
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestConfirmStatement:
    def test_confirm_changes_status_and_sets_confirmed_fields(
        self, api_client, finance_user, customer
    ):
        """Confirming a draft statement updates status, confirmed_by, confirmed_at."""
        statement = MonthlyStatement.objects.create(
            customer=customer, year=2025, month=8, total_amount=Decimal('5000.00'),
        )

        api_client.force_authenticate(user=finance_user)
        response = api_client.patch(f'/api/v1/statements/{statement.id}/confirm/')

        assert response.status_code == status.HTTP_200_OK
        data = response.data
        assert data['status'] == 'confirmed'
        assert data['confirmed_by'] == finance_user.id
        assert data['confirmed_at'] is not None

    def test_confirm_auto_creates_receivable(
        self, api_client, finance_user, customer
    ):
        """Confirming a statement creates a linked Receivable."""
        statement = MonthlyStatement.objects.create(
            customer=customer, year=2025, month=9, total_amount=Decimal('8000.00'),
        )

        api_client.force_authenticate(user=finance_user)
        api_client.patch(f'/api/v1/statements/{statement.id}/confirm/')

        receivable = Receivable.objects.get(customer=customer, year=2025, month=9)
        assert receivable.total_amount == Decimal('8000.00')
        assert receivable.receivable_no.startswith('AR')

    def test_confirm_non_draft_returns_error(
        self, api_client, finance_user, customer
    ):
        """Attempting to confirm an already-confirmed statement returns 400."""
        statement = MonthlyStatement.objects.create(
            customer=customer, year=2025, month=10, total_amount=Decimal('3000.00'),
            status='confirmed',
        )

        api_client.force_authenticate(user=finance_user)
        response = api_client.patch(f'/api/v1/statements/{statement.id}/confirm/')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert '草稿' in response.data['detail']

    def test_confirm_updates_existing_receivable(
        self, api_client, finance_user, customer
    ):
        """If a receivable already exists for that month it gets updated, not duplicated."""
        Receivable.objects.create(
            customer=customer, year=2025, month=11, total_amount=Decimal('1000.00'),
            due_date=date(2025, 12, 31),
        )
        statement = MonthlyStatement.objects.create(
            customer=customer, year=2025, month=11, total_amount=Decimal('9500.00'),
        )

        api_client.force_authenticate(user=finance_user)
        api_client.patch(f'/api/v1/statements/{statement.id}/confirm/')

        # Should still be only one receivable for that month
        assert Receivable.objects.filter(customer=customer, year=2025, month=11).count() == 1
        r = Receivable.objects.get(customer=customer, year=2025, month=11)
        assert r.total_amount == Decimal('9500.00')


# ---------------------------------------------------------------------------
# Detail includes orders list
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestStatementDetail:
    def test_detail_includes_orders_list(
        self, api_client, finance_user, customer, plating_process
    ):
        """Retrieving a statement detail returns the nested orders."""
        o1 = make_order(customer, plating_process, '600.00', 2025, 3)
        o2 = make_order(customer, plating_process, '400.00', 2025, 3)
        statement = MonthlyStatement.objects.create(
            customer=customer, year=2025, month=3, total_amount=Decimal('1000.00'),
        )
        statement.orders.set([o1, o2])

        api_client.force_authenticate(user=finance_user)
        response = api_client.get(f'/api/v1/statements/{statement.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['orders']) == 2
        order_nos = {o['order_no'] for o in response.data['orders']}
        assert o1.order_no in order_nos
        assert o2.order_no in order_nos


# ---------------------------------------------------------------------------
# List statements
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestStatementList:
    def test_list_statements(self, api_client, finance_user, customer, plating_process):
        """List returns all statements with order_count."""
        s1 = MonthlyStatement.objects.create(
            customer=customer, year=2025, month=1, total_amount=Decimal('1000.00'),
        )
        o = make_order(customer, plating_process, '1000.00', 2025, 1)
        s1.orders.add(o)

        MonthlyStatement.objects.create(
            customer=customer, year=2025, month=2, total_amount=Decimal('2000.00'),
        )

        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/statements/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

        # Find the statement with orders
        results = response.data['results']
        stmt_with_order = next(r for r in results if r['month'] == 1)
        assert stmt_with_order['order_count'] == 1
        assert stmt_with_order['customer_name'] == 'ABC电子'
        assert stmt_with_order['status_display'] == '草稿'

    def test_list_filter_by_status(self, api_client, finance_user, customer):
        """Filter statements by status."""
        MonthlyStatement.objects.create(
            customer=customer, year=2025, month=1, total_amount=Decimal('1000.00'),
            status='draft',
        )
        MonthlyStatement.objects.create(
            customer=customer, year=2025, month=2, total_amount=Decimal('2000.00'),
            status='confirmed',
        )

        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/statements/', {'status': 'draft'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['status'] == 'draft'

    def test_workshop_user_cannot_list_statements(self, api_client, workshop_user):
        """Workshop role is forbidden from the statements endpoint."""
        api_client.force_authenticate(user=workshop_user)
        response = api_client.get('/api/v1/statements/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_returns_401(self, api_client):
        response = api_client.get('/api/v1/statements/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
