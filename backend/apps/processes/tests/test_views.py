import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.processes.models import PlatingProcess, PricingRule
from apps.customers.models import Customer

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
def inactive_process(db):
    return PlatingProcess.objects.create(
        name='旧工艺',
        code='OLD001',
        unit='piece',
        base_price=Decimal('2.00'),
        is_active=False,
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
def pricing_rule(db, plating_process, customer):
    return PricingRule.objects.create(
        customer=customer,
        plating_process=plating_process,
        unit_price=Decimal('4.5000'),
        min_charge=Decimal('50.00'),
        effective_date='2024-01-01',
        remark='客户专属价',
    )


# ---------------------------------------------------------------------------
# PlatingProcess API tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestPlatingProcessList:
    def test_list_active_processes_only_by_default(self, api_client, finance_user, plating_process, inactive_process):
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/processes/')
        assert response.status_code == status.HTTP_200_OK
        codes = [r['code'] for r in response.data['results']]
        assert 'ZN001' in codes
        assert 'OLD001' not in codes

    def test_list_all_with_is_active_param(self, api_client, finance_user, plating_process, inactive_process):
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/processes/', {'is_active': ''})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2

    def test_search_by_name(self, api_client, finance_user, plating_process):
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/processes/', {'search': '镀锌'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['name'] == '镀锌'

    def test_search_by_code(self, api_client, finance_user, plating_process):
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/processes/', {'search': 'ZN001'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_unauthenticated_cannot_list(self, api_client):
        response = api_client.get('/api/v1/processes/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPlatingProcessCreate:
    def test_finance_can_create(self, api_client, finance_user):
        api_client.force_authenticate(user=finance_user)
        data = {
            'name': '镀铬',
            'code': 'CR001',
            'unit': 'area',
            'base_price': '8.50',
            'description': '硬铬工艺',
        }
        response = api_client.post('/api/v1/processes/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['name'] == '镀铬'
        assert response.data['code'] == 'CR001'
        assert PlatingProcess.objects.count() == 1

    def test_workshop_cannot_create(self, api_client, workshop_user):
        api_client.force_authenticate(user=workshop_user)
        data = {'name': '镀铜', 'code': 'CU001', 'unit': 'area', 'base_price': '3.00'}
        response = api_client.post('/api/v1/processes/', data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_missing_required_fields(self, api_client, finance_user):
        api_client.force_authenticate(user=finance_user)
        response = api_client.post('/api/v1/processes/', {'name': '镀铬'})  # missing code
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_duplicate_code_rejected(self, api_client, finance_user, plating_process):
        api_client.force_authenticate(user=finance_user)
        data = {'name': '镀锌2', 'code': 'ZN001', 'unit': 'area', 'base_price': '5.00'}
        response = api_client.post('/api/v1/processes/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPlatingProcessDetail:
    def test_retrieve_process(self, api_client, finance_user, plating_process):
        api_client.force_authenticate(user=finance_user)
        response = api_client.get(f'/api/v1/processes/{plating_process.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == 'ZN001'
        assert response.data['name'] == '镀锌'

    def test_update_process(self, api_client, finance_user, plating_process):
        api_client.force_authenticate(user=finance_user)
        data = {
            'name': '镀锌（更新）',
            'code': 'ZN001',
            'unit': 'area',
            'base_price': '6.00',
        }
        response = api_client.put(f'/api/v1/processes/{plating_process.id}/', data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['base_price'] == '6.00'
        assert response.data['name'] == '镀锌（更新）'

    def test_partial_update_process(self, api_client, finance_user, plating_process):
        api_client.force_authenticate(user=finance_user)
        response = api_client.patch(f'/api/v1/processes/{plating_process.id}/', {'base_price': '7.50'})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['base_price'] == '7.50'

    def test_workshop_cannot_update(self, api_client, workshop_user, plating_process):
        api_client.force_authenticate(user=workshop_user)
        response = api_client.patch(f'/api/v1/processes/{plating_process.id}/', {'base_price': '9.00'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_process(self, api_client, finance_user, plating_process):
        api_client.force_authenticate(user=finance_user)
        response = api_client.delete(f'/api/v1/processes/{plating_process.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert PlatingProcess.objects.count() == 0

    def test_workshop_cannot_delete(self, api_client, workshop_user, plating_process):
        api_client.force_authenticate(user=workshop_user)
        response = api_client.delete(f'/api/v1/processes/{plating_process.id}/')
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ---------------------------------------------------------------------------
# PricingRule API tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestPricingRuleList:
    def test_list_pricing_rules(self, api_client, finance_user, pricing_rule):
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/pricing-rules/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['customer_name'] == 'ABC电子'
        assert response.data['results'][0]['process_name'] == '镀锌'

    def test_filter_by_customer(self, api_client, finance_user, pricing_rule, customer, plating_process):
        # Create a generic rule
        PricingRule.objects.create(
            customer=None,
            plating_process=plating_process,
            unit_price=Decimal('5.0000'),
            effective_date='2024-01-01',
        )
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/pricing-rules/', {'customer': customer.id})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_filter_by_process(self, api_client, finance_user, pricing_rule, plating_process):
        api_client.force_authenticate(user=finance_user)
        response = api_client.get('/api/v1/pricing-rules/', {'plating_process': plating_process.id})
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_unauthenticated_cannot_list(self, api_client):
        response = api_client.get('/api/v1/pricing-rules/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPricingRuleCreate:
    def test_create_with_customer(self, api_client, finance_user, plating_process, customer):
        api_client.force_authenticate(user=finance_user)
        data = {
            'customer': customer.id,
            'plating_process': plating_process.id,
            'unit_price': '4.2500',
            'min_charge': '30.00',
            'effective_date': '2024-06-01',
            'remark': '合同价',
        }
        response = api_client.post('/api/v1/pricing-rules/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['customer'] == customer.id
        assert response.data['customer_name'] == 'ABC电子'
        assert response.data['process_name'] == '镀锌'
        assert PricingRule.objects.count() == 1

    def test_create_generic_rule(self, api_client, finance_user, plating_process):
        api_client.force_authenticate(user=finance_user)
        data = {
            'plating_process': plating_process.id,
            'unit_price': '5.0000',
            'effective_date': '2024-01-01',
        }
        response = api_client.post('/api/v1/pricing-rules/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['customer'] is None

    def test_workshop_cannot_create(self, api_client, workshop_user, plating_process):
        api_client.force_authenticate(user=workshop_user)
        data = {
            'plating_process': plating_process.id,
            'unit_price': '5.0000',
            'effective_date': '2024-01-01',
        }
        response = api_client.post('/api/v1/pricing-rules/', data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_missing_required_fields(self, api_client, finance_user):
        api_client.force_authenticate(user=finance_user)
        response = api_client.post('/api/v1/pricing-rules/', {'unit_price': '5.00'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPricingRuleDetail:
    def test_retrieve_rule(self, api_client, finance_user, pricing_rule):
        api_client.force_authenticate(user=finance_user)
        response = api_client.get(f'/api/v1/pricing-rules/{pricing_rule.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['unit_price'] == '4.5000'
        assert response.data['remark'] == '客户专属价'

    def test_update_rule(self, api_client, finance_user, pricing_rule, customer, plating_process):
        api_client.force_authenticate(user=finance_user)
        data = {
            'customer': customer.id,
            'plating_process': plating_process.id,
            'unit_price': '3.9000',
            'min_charge': '60.00',
            'effective_date': '2024-03-01',
        }
        response = api_client.put(f'/api/v1/pricing-rules/{pricing_rule.id}/', data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['unit_price'] == '3.9000'

    def test_workshop_cannot_update(self, api_client, workshop_user, pricing_rule, customer, plating_process):
        api_client.force_authenticate(user=workshop_user)
        data = {
            'customer': customer.id,
            'plating_process': plating_process.id,
            'unit_price': '3.9000',
            'effective_date': '2024-03-01',
        }
        response = api_client.put(f'/api/v1/pricing-rules/{pricing_rule.id}/', data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_rule(self, api_client, finance_user, pricing_rule):
        api_client.force_authenticate(user=finance_user)
        response = api_client.delete(f'/api/v1/pricing-rules/{pricing_rule.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert PricingRule.objects.count() == 0
