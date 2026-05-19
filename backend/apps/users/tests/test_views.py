import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        real_name='测试',
        role='finance',
        phone='13800138000',
    )


@pytest.mark.django_db
class TestLogin:
    def test_login_success(self, api_client, user):
        response = api_client.post('/api/v1/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123',
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['username'] == 'testuser'
        assert response.data['user']['role'] == 'finance'

    def test_login_wrong_password(self, api_client, user):
        response = api_client.post('/api/v1/auth/login/', {
            'username': 'testuser',
            'password': 'wrongpass',
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_missing_fields(self, api_client):
        response = api_client.post('/api/v1/auth/login/', {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestMe:
    def test_get_current_user(self, api_client, user):
        api_client.force_authenticate(user=user)
        response = api_client.get('/api/v1/auth/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'testuser'
        assert response.data['real_name'] == '测试'
        assert response.data['role'] == 'finance'

    def test_unauthenticated(self, api_client):
        response = api_client.get('/api/v1/auth/me/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
