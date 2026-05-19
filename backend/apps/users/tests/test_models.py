import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            real_name='测试用户',
            role='finance',
            phone='13800138000',
        )
        assert user.username == 'testuser'
        assert user.real_name == '测试用户'
        assert user.role == 'finance'
        assert user.phone == '13800138000'
        assert user.is_active is True
        assert user.check_password('testpass123')

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            username='admin',
            password='admin123',
            real_name='管理员',
        )
        assert user.is_staff is True
        assert user.is_superuser is True
        assert user.role == 'boss'

    def test_role_choices(self):
        user = User(username='t', role='invalid')
        assert user.role not in dict(User.ROLE_CHOICES)
