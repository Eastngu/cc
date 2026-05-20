import pytest
from decimal import Decimal
from datetime import date
from django.contrib.auth import get_user_model
from apps.customers.models import Customer
from apps.finance.models import Receivable, Payable, Payment

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
def finance_user(db):
    return User.objects.create_user(
        username='finance1', password='pass123', role='finance', real_name='财务员',
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
# Receivable model tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestReceivableModel:
    def test_creation(self, receivable, customer):
        assert receivable.pk is not None
        assert receivable.customer == customer
        assert receivable.year == 2025
        assert receivable.month == 1

    def test_auto_receivable_no(self, receivable, customer):
        expected = f"AR2025{1:02d}{customer.id:04d}"
        assert receivable.receivable_no == expected

    def test_auto_balance_on_create(self, receivable):
        assert receivable.balance == Decimal('10000.00')

    def test_status_open_on_create(self, receivable):
        assert receivable.status == 'open'

    def test_status_partial_when_partial_payment(self, receivable):
        receivable.received_amount = Decimal('3000.00')
        receivable.save()
        assert receivable.status == 'partial'
        assert receivable.balance == Decimal('7000.00')

    def test_status_settled_when_fully_paid(self, receivable):
        receivable.received_amount = Decimal('10000.00')
        receivable.save()
        assert receivable.status == 'settled'
        assert receivable.balance == Decimal('0')

    def test_balance_zero_when_overpaid(self, receivable):
        receivable.received_amount = Decimal('12000.00')
        receivable.save()
        assert receivable.status == 'settled'
        assert receivable.balance == Decimal('0')

    def test_str(self, receivable, customer):
        assert str(receivable.receivable_no) in str(receivable)

    def test_unique_together_customer_year_month(self, customer):
        Receivable.objects.create(
            customer=customer, year=2025, month=3,
            total_amount=Decimal('5000.00'), due_date=date(2025, 4, 30),
        )
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            Receivable.objects.create(
                customer=customer, year=2025, month=3,
                total_amount=Decimal('3000.00'), due_date=date(2025, 4, 30),
            )


# ---------------------------------------------------------------------------
# Payable model tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestPayableModel:
    def test_creation(self, payable):
        assert payable.pk is not None
        assert payable.supplier_name == '广州电力公司'
        assert payable.category == 'electricity'

    def test_auto_payable_no(self, payable):
        assert payable.payable_no.startswith('AP')
        assert len(payable.payable_no) > 4

    def test_auto_balance_on_create(self, payable):
        assert payable.balance == Decimal('5000.00')

    def test_status_open_on_create(self, payable):
        assert payable.status == 'open'

    def test_status_partial_when_partial_payment(self, payable):
        payable.paid_amount = Decimal('2000.00')
        payable.save()
        assert payable.status == 'partial'
        assert payable.balance == Decimal('3000.00')

    def test_status_settled_when_fully_paid(self, payable):
        payable.paid_amount = Decimal('5000.00')
        payable.save()
        assert payable.status == 'settled'
        assert payable.balance == Decimal('0')

    def test_payable_no_sequential(self, db):
        p1 = Payable.objects.create(
            supplier_name='供应商A', category='material',
            total_amount=Decimal('1000.00'), due_date=date(2025, 3, 31),
        )
        p2 = Payable.objects.create(
            supplier_name='供应商B', category='material',
            total_amount=Decimal('2000.00'), due_date=date(2025, 3, 31),
        )
        # Both should have the same prefix, different numbers
        assert p1.payable_no[:8] == p2.payable_no[:8]
        assert p1.payable_no != p2.payable_no

    def test_str(self, payable):
        assert payable.payable_no in str(payable)
        assert payable.supplier_name in str(payable)


# ---------------------------------------------------------------------------
# Payment model tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestPaymentModel:
    def test_creation_receive(self, receivable, customer, finance_user):
        payment = Payment.objects.create(
            type='receive',
            customer=customer,
            receivable=receivable,
            amount=Decimal('3000.00'),
            payment_date=date(2025, 1, 20),
            created_by=finance_user,
        )
        assert payment.pk is not None
        assert payment.type == 'receive'
        assert payment.amount == Decimal('3000.00')

    def test_auto_payment_no(self, receivable, customer, finance_user):
        payment = Payment.objects.create(
            type='receive',
            customer=customer,
            receivable=receivable,
            amount=Decimal('1000.00'),
            payment_date=date(2025, 1, 20),
            created_by=finance_user,
        )
        assert payment.payment_no.startswith('PY')
        assert len(payment.payment_no) > 4

    def test_payment_no_sequential(self, receivable, customer, finance_user):
        p1 = Payment.objects.create(
            type='receive', customer=customer, receivable=receivable,
            amount=Decimal('1000.00'), payment_date=date(2025, 1, 20),
        )
        p2 = Payment.objects.create(
            type='receive', customer=customer, receivable=receivable,
            amount=Decimal('2000.00'), payment_date=date(2025, 1, 20),
        )
        assert p1.payment_no[:10] == p2.payment_no[:10]
        assert p1.payment_no != p2.payment_no

    def test_payment_updates_receivable_received_amount(self, receivable, customer):
        Payment.objects.create(
            type='receive',
            customer=customer,
            receivable=receivable,
            amount=Decimal('4000.00'),
            payment_date=date(2025, 1, 20),
        )
        receivable.refresh_from_db()
        assert receivable.received_amount == Decimal('4000.00')
        assert receivable.status == 'partial'
        assert receivable.balance == Decimal('6000.00')

    def test_payment_settles_receivable(self, receivable, customer):
        Payment.objects.create(
            type='receive',
            customer=customer,
            receivable=receivable,
            amount=Decimal('10000.00'),
            payment_date=date(2025, 1, 25),
        )
        receivable.refresh_from_db()
        assert receivable.status == 'settled'
        assert receivable.balance == Decimal('0')

    def test_multiple_payments_accumulate_on_receivable(self, receivable, customer):
        Payment.objects.create(
            type='receive', customer=customer, receivable=receivable,
            amount=Decimal('3000.00'), payment_date=date(2025, 1, 10),
        )
        Payment.objects.create(
            type='receive', customer=customer, receivable=receivable,
            amount=Decimal('4000.00'), payment_date=date(2025, 1, 20),
        )
        receivable.refresh_from_db()
        assert receivable.received_amount == Decimal('7000.00')
        assert receivable.balance == Decimal('3000.00')
        assert receivable.status == 'partial'

    def test_payment_updates_payable_paid_amount(self, payable):
        Payment.objects.create(
            type='pay',
            payable=payable,
            amount=Decimal('2000.00'),
            payment_date=date(2025, 2, 10),
        )
        payable.refresh_from_db()
        assert payable.paid_amount == Decimal('2000.00')
        assert payable.status == 'partial'
        assert payable.balance == Decimal('3000.00')

    def test_payment_settles_payable(self, payable):
        Payment.objects.create(
            type='pay',
            payable=payable,
            amount=Decimal('5000.00'),
            payment_date=date(2025, 2, 15),
        )
        payable.refresh_from_db()
        assert payable.status == 'settled'
        assert payable.balance == Decimal('0')

    def test_str(self, receivable, customer):
        payment = Payment.objects.create(
            type='receive', customer=customer, receivable=receivable,
            amount=Decimal('1000.00'), payment_date=date(2025, 1, 15),
        )
        s = str(payment)
        assert payment.payment_no in s
