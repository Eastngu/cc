import pytest
from decimal import Decimal
from datetime import date
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.customers.models import Customer
from apps.finance.models import Receivable, Payable, Payment

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
        username='finance1', password='pass123', role='finance', real_name='财务员',
    )


@pytest.fixture
def boss_user(db):
    return User.objects.create_user(
        username='boss1', password='pass123', role='boss', real_name='老板',
    )


@pytest.fixture
def workshop_user(db):
    return User.objects.create_user(
        username='workshop1', password='pass123', role='workshop', real_name='车间主管',
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
def receivable(db, customer):
    return Receivable.objects.create(
        customer=customer,
        year=2025,
        month=1,
        total_amount=Decimal('10000.00'),
        due_date=date(2025, 2, 28),
    )


@pytest.fixture
def payable(db):
    return Payable.objects.create(
        supplier_name='广州电力公司',
        category='electricity',
        total_amount=Decimal('5000.00'),
        due_date=date(2025, 2, 15),
    )


# ---------------------------------------------------------------------------
# Receivable views
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestReceivableList:
    def test_list_receivables_finance_user(self, api_client, finance_user, receivable):
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/receivables/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        result = response.data['results'][0]
        assert result['receivable_no'] == receivable.receivable_no
        assert result['customer_name'] == 'ABC电子'
        assert result['status_display'] == '未结'

    def test_list_receivables_boss_user(self, api_client, boss_user, receivable):
        api_client.force_authenticate(user=boss_user)
        response = api_client.get('/api/v1/receivables/')
        assert response.status_code == status.HTTP_200_OK

    def test_list_receivables_unauthenticated(self, api_client):
        response = api_client.get('/api/v1/receivables/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_workshop_user_gets_403(self, api_client, workshop_user, receivable):
        api_client.force_authenticate(user=workshop_user)
        response = api_client.get('/api/v1/receivables/')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestReceivableCreate:
    def test_create_receivable(self, api_client, finance_user, customer):
        api_client.force_authenticate(user=finance_user)
        data = {
            'customer': customer.id,
            'year': 2025,
            'month': 6,
            'total_amount': '8000.00',
            'due_date': '2025-07-31',
        }
        response = api_client.post('/api/v1/receivables/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['total_amount'] == '8000.00'
        assert response.data['balance'] == '8000.00'
        assert response.data['status'] == 'open'
        assert response.data['receivable_no'].startswith('AR')

    def test_create_receivable_workshop_forbidden(self, api_client, workshop_user, customer):
        api_client.force_authenticate(user=workshop_user)
        data = {
            'customer': customer.id,
            'year': 2025,
            'month': 7,
            'total_amount': '5000.00',
            'due_date': '2025-08-31',
        }
        response = api_client.post('/api/v1/receivables/', data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_missing_required_fields(self, api_client, finance_user):
        api_client.force_authenticate(user=finance_user)
        response = api_client.post('/api/v1/receivables/', {'year': 2025})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestReceivableFilter:
    def test_filter_by_status(self, api_client, finance_user, customer):
        r1 = Receivable.objects.create(
            customer=customer, year=2025, month=1,
            total_amount=Decimal('5000.00'), due_date=date(2025, 2, 28),
        )
        # Create a second customer for different month
        customer2 = Customer.objects.create(
            name='其他公司', short_name='其他', payment_terms=30, default_billing_type='area',
        )
        r2 = Receivable.objects.create(
            customer=customer2, year=2025, month=1,
            total_amount=Decimal('3000.00'), due_date=date(2025, 2, 28),
        )
        r2.received_amount = Decimal('3000.00')
        r2.save()

        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/receivables/', {'status': 'open'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_filter_by_year_month(self, api_client, finance_user, customer):
        Receivable.objects.create(
            customer=customer, year=2025, month=1,
            total_amount=Decimal('5000.00'), due_date=date(2025, 2, 28),
        )
        customer2 = Customer.objects.create(
            name='另一客户', short_name='另一', payment_terms=30, default_billing_type='area',
        )
        Receivable.objects.create(
            customer=customer2, year=2025, month=2,
            total_amount=Decimal('4000.00'), due_date=date(2025, 3, 31),
        )
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/receivables/', {'year': 2025, 'month': 1})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1


# ---------------------------------------------------------------------------
# Payable views
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestPayableList:
    def test_list_payables(self, api_client, finance_user, payable):
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/payables/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        result = response.data['results'][0]
        assert result['supplier_name'] == '广州电力公司'
        assert result['status_display'] == '未付'
        assert result['category_display'] == '电费'

    def test_workshop_user_gets_403(self, api_client, workshop_user, payable):
        api_client.force_authenticate(user=workshop_user)
        response = api_client.get('/api/v1/payables/')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestPayableCreate:
    def test_create_payable(self, api_client, finance_user):
        api_client.force_authenticate(user=finance_user)
        data = {
            'supplier_name': '北京钢铁有限公司',
            'category': 'material',
            'total_amount': '20000.00',
            'due_date': '2025-03-31',
        }
        response = api_client.post('/api/v1/payables/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['supplier_name'] == '北京钢铁有限公司'
        assert response.data['balance'] == '20000.00'
        assert response.data['status'] == 'open'
        assert response.data['payable_no'].startswith('AP')

    def test_create_payable_with_remark(self, api_client, finance_user):
        api_client.force_authenticate(user=finance_user)
        data = {
            'supplier_name': '设备供应商',
            'category': 'equipment',
            'total_amount': '50000.00',
            'due_date': '2025-06-30',
            'remark': '购买镀锌生产线设备',
        }
        response = api_client.post('/api/v1/payables/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['remark'] == '购买镀锌生产线设备'


@pytest.mark.django_db
class TestPayableFilter:
    def test_filter_by_category(self, api_client, finance_user):
        Payable.objects.create(
            supplier_name='电力公司', category='electricity',
            total_amount=Decimal('3000.00'), due_date=date(2025, 2, 28),
        )
        Payable.objects.create(
            supplier_name='原料供应商', category='material',
            total_amount=Decimal('8000.00'), due_date=date(2025, 3, 31),
        )
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/payables/', {'category': 'electricity'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['category'] == 'electricity'


# ---------------------------------------------------------------------------
# Payment views
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestPaymentReceive:
    def test_create_receive_payment_updates_receivable(
        self, api_client, finance_user, customer, receivable
    ):
        api_client.force_authenticate(user=finance_user)
        data = {
            'type': 'receive',
            'customer': customer.id,
            'receivable': receivable.id,
            'amount': '4000.00',
            'payment_method': 'transfer',
            'payment_date': '2025-01-20',
        }
        response = api_client.post('/api/v1/payments/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['payment_no'].startswith('PY')
        assert response.data['type_display'] == '收款'

        # Verify receivable was updated
        receivable.refresh_from_db()
        assert receivable.received_amount == Decimal('4000.00')
        assert receivable.status == 'partial'

    def test_create_receive_payment_sets_created_by(
        self, api_client, finance_user, customer, receivable
    ):
        api_client.force_authenticate(user=finance_user)
        data = {
            'type': 'receive',
            'customer': customer.id,
            'receivable': receivable.id,
            'amount': '1000.00',
            'payment_method': 'cash',
            'payment_date': '2025-01-15',
        }
        response = api_client.post('/api/v1/payments/', data)
        assert response.status_code == status.HTTP_201_CREATED
        payment = Payment.objects.get(id=response.data['id'])
        assert payment.created_by == finance_user

    def test_full_settlement_via_payment(
        self, api_client, finance_user, customer, receivable
    ):
        api_client.force_authenticate(user=finance_user)
        data = {
            'type': 'receive',
            'customer': customer.id,
            'receivable': receivable.id,
            'amount': '10000.00',
            'payment_method': 'transfer',
            'payment_date': '2025-01-31',
        }
        api_client.post('/api/v1/payments/', data)
        receivable.refresh_from_db()
        assert receivable.status == 'settled'
        assert receivable.balance == Decimal('0')


@pytest.mark.django_db
class TestPaymentPay:
    def test_create_pay_payment_updates_payable(
        self, api_client, finance_user, payable
    ):
        api_client.force_authenticate(user=finance_user)
        data = {
            'type': 'pay',
            'payable': payable.id,
            'amount': '2000.00',
            'payment_method': 'transfer',
            'payment_date': '2025-02-10',
        }
        response = api_client.post('/api/v1/payments/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['type_display'] == '付款'

        payable.refresh_from_db()
        assert payable.paid_amount == Decimal('2000.00')
        assert payable.status == 'partial'

    def test_full_payment_settles_payable(
        self, api_client, finance_user, payable
    ):
        api_client.force_authenticate(user=finance_user)
        data = {
            'type': 'pay',
            'payable': payable.id,
            'amount': '5000.00',
            'payment_method': 'acceptance',
            'payment_date': '2025-02-15',
        }
        api_client.post('/api/v1/payments/', data)
        payable.refresh_from_db()
        assert payable.status == 'settled'
        assert payable.balance == Decimal('0')


@pytest.mark.django_db
class TestPaymentList:
    def test_list_payments(self, api_client, finance_user, customer, receivable):
        Payment.objects.create(
            type='receive', customer=customer, receivable=receivable,
            amount=Decimal('5000.00'), payment_date=date(2025, 1, 10),
        )
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/payments/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_filter_payments_by_type(self, api_client, finance_user, customer, receivable, payable):
        Payment.objects.create(
            type='receive', customer=customer, receivable=receivable,
            amount=Decimal('3000.00'), payment_date=date(2025, 1, 10),
        )
        Payment.objects.create(
            type='pay', payable=payable,
            amount=Decimal('2000.00'), payment_date=date(2025, 1, 15),
        )
        api_client.force_authenticate(user=finance_user)

        response = api_client.get('/api/v1/payments/', {'type': 'receive'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['type'] == 'receive'

    def test_workshop_user_cannot_list_payments(self, api_client, workshop_user):
        api_client.force_authenticate(user=workshop_user)
        response = api_client.get('/api/v1/payments/')
        assert response.status_code == status.HTTP_403_FORBIDDEN
