import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.customers.models import Customer

User = get_user_model()


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
def sample_customer(db):
    return Customer.objects.create(
        name='深圳市ABC电子有限公司',
        short_name='ABC电子',
        contact_person='张三',
        phone='13900139000',
        payment_terms=30,
        default_billing_type='area',
    )


@pytest.mark.django_db
class TestCustomerList:
    def test_list_customers(self, api_client, finance_user, sample_customer):
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/customers/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['name'] == '深圳市ABC电子有限公司'

    def test_search_customers(self, api_client, finance_user, sample_customer):
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/customers/', {'search': 'ABC'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_unauthenticated(self, api_client):
        response = api_client.get('/api/v1/customers/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCustomerCreate:
    def test_create_customer(self, api_client, finance_user):
        api_client.force_authenticate(user=finance_user)
        data = {
            'name': '东莞市XYZ五金厂',
            'short_name': 'XYZ五金',
            'contact_person': '李四',
            'phone': '13800138001',
            'payment_terms': 60,
            'default_billing_type': 'weight',
        }
        response = api_client.post('/api/v1/customers/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == '东莞市XYZ五金厂'
        assert Customer.objects.count() == 1

    def test_create_missing_name(self, api_client, finance_user):
        api_client.force_authenticate(user=finance_user)
        response = api_client.post('/api/v1/customers/', {'short_name': 'X'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_workshop_cannot_create(self, api_client, workshop_user):
        api_client.force_authenticate(user=workshop_user)
        data = {'name': '测试公司', 'short_name': '测试'}
        response = api_client.post('/api/v1/customers/', data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCustomerUpdate:
    def test_update_customer(self, api_client, finance_user, sample_customer):
        api_client.force_authenticate(user=finance_user)
        response = api_client.put(
            f'/api/v1/customers/{sample_customer.id}/',
            {
                'name': '深圳市ABC电子有限公司',
                'short_name': 'ABC',
                'contact_person': '张三',
                'phone': '13900139000',
                'payment_terms': 60,
                'default_billing_type': 'area',
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['payment_terms'] == 60


@pytest.mark.django_db
class TestCustomerDelete:
    def test_soft_delete(self, api_client, finance_user, sample_customer):
        api_client.force_authenticate(user=finance_user)
        response = api_client.delete(f'/api/v1/customers/{sample_customer.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        sample_customer.refresh_from_db()
        assert sample_customer.is_active is False
