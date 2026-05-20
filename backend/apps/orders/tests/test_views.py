import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from apps.customers.models import Customer
from apps.processes.models import PlatingProcess
from apps.orders.models import Order

User = get_user_model()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

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
        unit_price=Decimal('4.5000'),
        total_amount=Decimal('900.00'),
        created_by=finance_user,
    )


@pytest.fixture
def order_data(customer, plating_process):
    return {
        'customer': customer.id,
        'plating_process': plating_process.id,
        'product_name': '铜质接头',
        'product_spec': 'M10x20',
        'quantity': '150.00',
        'unit': 'dm²',
        'unit_price': '3.5000',
        'total_amount': '525.00',
    }


# ---------------------------------------------------------------------------
# List / retrieve
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestOrderList:
    def test_list_orders_authenticated(self, api_client, finance_user, sample_order):
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/orders/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        result = response.data['results'][0]
        assert result['order_no'] == sample_order.order_no
        assert result['customer_name'] == 'ABC电子'
        assert result['process_name'] == '镀锌'
        assert result['status_display'] == '待加工'

    def test_unauthenticated_returns_401(self, api_client):
        response = api_client.get('/api/v1/orders/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_uses_list_serializer_fields(self, api_client, finance_user, sample_order):
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/orders/')
        result = response.data['results'][0]
        # List serializer should NOT include completed_at/remark
        assert 'completed_at' not in result
        assert 'remark' not in result


@pytest.mark.django_db
class TestOrderCreate:
    def test_create_order(self, api_client, finance_user, order_data):
        api_client.force_authenticate(user=finance_user)
        response = api_client.post('/api/v1/orders/', order_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['product_name'] == '铜质接头'
        assert response.data['order_no'].startswith('DD')
        assert response.data['status'] == 'pending'
        assert Order.objects.count() == 1

    def test_create_sets_created_by(self, api_client, finance_user, order_data):
        api_client.force_authenticate(user=finance_user)
        response = api_client.post('/api/v1/orders/', order_data)
        assert response.status_code == status.HTTP_201_CREATED
        order = Order.objects.get(id=response.data['id'])
        assert order.created_by == finance_user

    def test_create_order_unauthenticated(self, api_client, order_data):
        response = api_client.post('/api/v1/orders/', order_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_missing_required_fields(self, api_client, finance_user):
        api_client.force_authenticate(user=finance_user)
        response = api_client.post('/api/v1/orders/', {'product_name': '只有名称'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_workshop_can_create(self, api_client, workshop_user, order_data):
        api_client.force_authenticate(user=workshop_user)
        response = api_client.post('/api/v1/orders/', order_data)
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestOrderFilter:
    def test_filter_by_status(self, api_client, finance_user, customer, plating_process):
        Order.objects.create(
            customer=customer, plating_process=plating_process,
            product_name='产品A', quantity=Decimal('100'), unit='dm²',
            unit_price=Decimal('5.0000'), total_amount=Decimal('500'),
            status='pending',
        )
        Order.objects.create(
            customer=customer, plating_process=plating_process,
            product_name='产品B', quantity=Decimal('50'), unit='dm²',
            unit_price=Decimal('5.0000'), total_amount=Decimal('250'),
            status='processing',
        )
        api_client.force_authenticate(user=finance_user)

        response = api_client.get('/api/v1/orders/', {'status': 'pending'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['status'] == 'pending'

    def test_filter_by_customer(self, api_client, finance_user, customer, plating_process):
        other_customer = Customer.objects.create(
            name='另一家公司', short_name='另一家', payment_terms=30, default_billing_type='area',
        )
        Order.objects.create(
            customer=customer, plating_process=plating_process,
            product_name='产品A', quantity=Decimal('100'), unit='dm²',
            unit_price=Decimal('5.0000'), total_amount=Decimal('500'),
        )
        Order.objects.create(
            customer=other_customer, plating_process=plating_process,
            product_name='产品B', quantity=Decimal('50'), unit='dm²',
            unit_price=Decimal('5.0000'), total_amount=Decimal('250'),
        )
        api_client.force_authenticate(user=finance_user)

        response = api_client.get('/api/v1/orders/', {'customer': customer.id})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_filter_by_plating_process(self, api_client, finance_user, customer, plating_process):
        other_process = PlatingProcess.objects.create(
            name='镀铬', code='CR001', unit='area', base_price=Decimal('8.00'),
        )
        Order.objects.create(
            customer=customer, plating_process=plating_process,
            product_name='产品A', quantity=Decimal('100'), unit='dm²',
            unit_price=Decimal('5.0000'), total_amount=Decimal('500'),
        )
        Order.objects.create(
            customer=customer, plating_process=other_process,
            product_name='产品B', quantity=Decimal('50'), unit='dm²',
            unit_price=Decimal('8.0000'), total_amount=Decimal('400'),
        )
        api_client.force_authenticate(user=finance_user)

        response = api_client.get('/api/v1/orders/', {'plating_process': plating_process.id})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1


@pytest.mark.django_db
class TestOrderSearch:
    def test_search_by_order_no(self, api_client, finance_user, sample_order):
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/orders/', {'search': sample_order.order_no})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_search_by_product_name(self, api_client, finance_user, sample_order):
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/orders/', {'search': '铝合金'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_search_no_match(self, api_client, finance_user, sample_order):
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/orders/', {'search': '不存在的产品XYZ'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0


@pytest.mark.django_db
class TestOrderChangeStatus:
    def test_change_status_to_processing(self, api_client, finance_user, sample_order):
        api_client.force_authenticate(user=finance_user)
        response = api_client.patch(
            f'/api/v1/orders/{sample_order.id}/status/',
            {'status': 'processing'},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'processing'
        sample_order.refresh_from_db()
        assert sample_order.status == 'processing'

    def test_change_status_to_completed_sets_completed_at(self, api_client, finance_user, sample_order):
        api_client.force_authenticate(user=finance_user)
        response = api_client.patch(
            f'/api/v1/orders/{sample_order.id}/status/',
            {'status': 'completed'},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'completed'
        sample_order.refresh_from_db()
        assert sample_order.completed_at == timezone.now().date()

    def test_change_status_to_shipped_sets_shipped_at(self, api_client, finance_user, sample_order):
        api_client.force_authenticate(user=finance_user)
        response = api_client.patch(
            f'/api/v1/orders/{sample_order.id}/status/',
            {'status': 'shipped'},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'shipped'
        sample_order.refresh_from_db()
        assert sample_order.shipped_at == timezone.now().date()

    def test_completed_at_not_overwritten_on_re_complete(self, api_client, finance_user, sample_order):
        from datetime import date
        original_date = date(2025, 1, 15)
        sample_order.completed_at = original_date
        sample_order.save()

        api_client.force_authenticate(user=finance_user)
        api_client.patch(
            f'/api/v1/orders/{sample_order.id}/status/',
            {'status': 'completed'},
        )
        sample_order.refresh_from_db()
        assert sample_order.completed_at == original_date

    def test_change_status_invalid_value(self, api_client, finance_user, sample_order):
        api_client.force_authenticate(user=finance_user)
        response = api_client.patch(
            f'/api/v1/orders/{sample_order.id}/status/',
            {'status': 'invalid_status'},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_status_unauthenticated(self, api_client, sample_order):
        response = api_client.patch(
            f'/api/v1/orders/{sample_order.id}/status/',
            {'status': 'processing'},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_change_status_response_contains_detail_fields(self, api_client, finance_user, sample_order):
        api_client.force_authenticate(user=finance_user)
        response = api_client.patch(
            f'/api/v1/orders/{sample_order.id}/status/',
            {'status': 'completed'},
        )
        assert response.status_code == status.HTTP_200_OK
        # Should return detail serializer fields
        assert 'completed_at' in response.data
        assert 'remark' in response.data
        assert 'created_by_name' in response.data


@pytest.mark.django_db
class TestOrderDetail:
    def test_retrieve_order(self, api_client, finance_user, sample_order):
        api_client.force_authenticate(user=finance_user)
        response = api_client.get(f'/api/v1/orders/{sample_order.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['order_no'] == sample_order.order_no
        assert response.data['product_name'] == '铝合金外壳'
        assert response.data['customer_name'] == 'ABC电子'
        assert 'completed_at' in response.data
        assert 'remark' in response.data

    def test_update_order(self, api_client, finance_user, sample_order, customer, plating_process):
        api_client.force_authenticate(user=finance_user)
        data = {
            'customer': customer.id,
            'plating_process': plating_process.id,
            'product_name': '更新后的产品名',
            'quantity': '300.00',
            'unit': 'dm²',
            'unit_price': '4.5000',
            'total_amount': '1350.00',
        }
        response = api_client.put(f'/api/v1/orders/{sample_order.id}/', data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['product_name'] == '更新后的产品名'

    def test_partial_update_order(self, api_client, finance_user, sample_order):
        api_client.force_authenticate(user=finance_user)
        response = api_client.patch(
            f'/api/v1/orders/{sample_order.id}/',
            {'remark': '客户要求加急处理'},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['remark'] == '客户要求加急处理'

    def test_delete_order(self, api_client, finance_user, sample_order):
        api_client.force_authenticate(user=finance_user)
        response = api_client.delete(f'/api/v1/orders/{sample_order.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Order.objects.count() == 0
