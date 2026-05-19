# Electroplating ERP Phase 1: Project Setup + Auth + Customer Management

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish project foundation with Django backend, Vue 3 frontend, user authentication (JWT), and customer CRUD management.

**Architecture:** Django + DRF backend with JWT auth serving a Vue 3 + Element Plus SPA. Backend uses split settings (base/dev/prod), modular Django apps under `apps/`. Frontend uses Vite, Pinia stores, and Axios with interceptors for auth. MySQL database.

**Tech Stack:** Python 3.11+, Django 4.2, DRF, simplejwt, MySQL, Vue 3, Vite, Element Plus, Pinia, Axios, ECharts (later phases)

---

## File Structure

### Backend

```
backend/
├── manage.py
├── requirements.txt
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py              # Shared settings (apps, middleware, DB, REST config)
│   │   ├── dev.py               # Debug, CORS allow-all, console email
│   │   └── prod.py              # Production overrides
│   ├── urls.py                  # Root URL conf
│   └── wsgi.py
├── apps/
│   ├── __init__.py
│   ├── users/
│   │   ├── __init__.py
│   │   ├── models.py            # Custom User model (role field)
│   │   ├── serializers.py       # User serializers, login/register
│   │   ├── views.py             # Auth views (login, refresh, me)
│   │   ├── urls.py
│   │   ├── permissions.py       # Role-based permission classes
│   │   ├── admin.py
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       ├── test_views.py
│   │       └── test_permissions.py
│   └── customers/
│       ├── __init__.py
│       ├── models.py            # Customer model
│       ├── serializers.py       # Customer CRUD serializers
│       ├── views.py             # Customer ViewSet
│       ├── urls.py
│       ├── admin.py
│       ├── filters.py           # Django-filter filtersets
│       └── tests/
│           ├── __init__.py
│           ├── test_models.py
│           └── test_views.py
```

### Frontend

```
frontend/
├── index.html
├── package.json
├── vite.config.js
├── src/
│   ├── main.js                  # App entry, Element Plus setup
│   ├── App.vue                  # Root component with router-view
│   ├── api/
│   │   ├── index.js             # Axios instance with interceptors
│   │   ├── auth.js              # Login, refresh, getMe
│   │   └── customers.js         # Customer CRUD API calls
│   ├── stores/
│   │   ├── auth.js              # Auth store (user, token, login/logout)
│   │   └── customers.js         # Customer list store
│   ├── router/
│   │   └── index.js             # Routes + navigation guards
│   ├── views/
│   │   ├── Login.vue            # Login page
│   │   ├── Layout.vue           # Main layout (sidebar + content)
│   │   ├── Dashboard.vue        # Placeholder dashboard
│   │   └── customers/
│   │       ├── CustomerList.vue # Customer table with search/filter
│   │       └── CustomerForm.vue # Create/edit customer dialog
│   └── utils/
│       └── format.js            # Date/currency formatters
```

---

## Task 1: Backend Project Scaffolding

**Files:**
- Create: `backend/manage.py`
- Create: `backend/requirements.txt`
- Create: `backend/config/__init__.py`
- Create: `backend/config/settings/__init__.py`
- Create: `backend/config/settings/base.py`
- Create: `backend/config/settings/dev.py`
- Create: `backend/config/urls.py`
- Create: `backend/config/wsgi.py`
- Create: `backend/apps/__init__.py`

- [ ] **Step 1: Create backend directory and requirements.txt**

```bash
mkdir -p backend
```

```txt
# backend/requirements.txt
Django==4.2.17
djangorestframework==3.15.2
djangorestframework-simplejwt==5.4.0
django-cors-headers==4.6.0
django-filter==24.3
mysqlclient==2.2.7
python-decouple==3.8
```

- [ ] **Step 2: Create manage.py**

```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
```

- [ ] **Step 3: Create config/settings/base.py**

```python
# backend/config/settings/base.py
import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'dev-secret-key-change-in-production')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'corsheaders',
    'django_filters',
    # Local apps
    'apps.users',
    'apps.customers',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'electroplating_erp'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', '127.0.0.1'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
        },
    }
}

AUTH_USER_MODEL = 'users.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# DRF
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
}

# JWT
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

- [ ] **Step 4: Create config/settings/dev.py**

```python
# backend/config/settings/dev.py
from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ['*']
CORS_ALLOW_ALL_ORIGINS = True
```

- [ ] **Step 5: Create config/settings/__init__.py and config/__init__.py**

```python
# backend/config/settings/__init__.py
# Settings package - use DJANGO_SETTINGS_MODULE to select env
```

```python
# backend/config/__init__.py
```

- [ ] **Step 6: Create config/urls.py**

```python
# backend/config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/customers/', include('apps.customers.urls')),
]
```

- [ ] **Step 7: Create config/wsgi.py**

```python
# backend/config/wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
application = get_wsgi_application()
```

- [ ] **Step 8: Create apps/__init__.py**

```python
# backend/apps/__init__.py
```

- [ ] **Step 9: Install dependencies and verify Django starts**

```bash
cd backend
pip install -r requirements.txt
python manage.py check
```

Expected: `System check identified no issues` (will have warnings about missing migrations, that's OK)

- [ ] **Step 10: Commit**

```bash
git add backend/
git commit -m "feat: scaffold Django backend with split settings and DRF config"
```

---

## Task 2: User Model and Authentication

**Files:**
- Create: `backend/apps/users/__init__.py`
- Create: `backend/apps/users/models.py`
- Create: `backend/apps/users/serializers.py`
- Create: `backend/apps/users/views.py`
- Create: `backend/apps/users/urls.py`
- Create: `backend/apps/users/permissions.py`
- Create: `backend/apps/users/admin.py`
- Create: `backend/apps/users/tests/__init__.py`
- Create: `backend/apps/users/tests/test_models.py`
- Create: `backend/apps/users/tests/test_views.py`

- [ ] **Step 1: Write the User model test**

```python
# backend/apps/users/tests/__init__.py
```

```python
# backend/apps/users/tests/test_models.py
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
        # Role field should only accept valid choices
        assert user.role not in dict(User.ROLE_CHOICES)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pip install pytest pytest-django
```

Create `backend/pytest.ini`:
```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.dev
python_files = tests.py test_*.py *_tests.py
```

```bash
pytest apps/users/tests/test_models.py -v
```

Expected: FAIL - `apps.users` models not defined yet

- [ ] **Step 3: Implement User model**

```python
# backend/apps/users/__init__.py
```

```python
# backend/apps/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('boss', '老板/管理层'),
        ('finance', '财务人员'),
        ('workshop', '车间主管'),
    ]

    real_name = models.CharField('姓名', max_length=20, blank=True)
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES, default='workshop')
    phone = models.CharField('手机号', max_length=11, blank=True)

    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.real_name}({self.username})'

    def save(self, *args, **kwargs):
        if self.is_superuser and not self.role:
            self.role = 'boss'
        super().save(*args, **kwargs)
```

- [ ] **Step 4: Create migrations and run model tests**

```bash
cd backend
python manage.py makemigrations users
python manage.py migrate
pytest apps/users/tests/test_models.py -v
```

Expected: All 3 tests PASS

- [ ] **Step 5: Write auth view tests**

```python
# backend/apps/users/tests/test_views.py
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
```

- [ ] **Step 6: Run auth view tests to verify they fail**

```bash
cd backend
pytest apps/users/tests/test_views.py -v
```

Expected: FAIL - views/urls not defined

- [ ] **Step 7: Implement serializers**

```python
# backend/apps/users/serializers.py
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'real_name', 'role', 'phone', 'is_active']
        read_only_fields = ['id']


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        user = authenticate(
            username=attrs['username'],
            password=attrs['password'],
        )
        if not user:
            raise serializers.ValidationError('用户名或密码错误')
        if not user.is_active:
            raise serializers.ValidationError('用户已被禁用')
        attrs['user'] = user
        return attrs
```

- [ ] **Step 8: Implement views**

```python
# backend/apps/users/views.py
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer, UserSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            if '用户名或密码错误' in str(serializer.errors):
                return Response(
                    {'detail': '用户名或密码错误'},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data,
        })


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
```

- [ ] **Step 9: Implement URLs**

```python
# backend/apps/users/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginView, MeView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', MeView.as_view(), name='me'),
]
```

- [ ] **Step 10: Implement permissions**

```python
# backend/apps/users/permissions.py
from rest_framework.permissions import BasePermission


class IsBoss(BasePermission):
    """Only boss/management can access."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'boss'


class IsFinance(BasePermission):
    """Only finance staff can access."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'finance'


class IsWorkshop(BasePermission):
    """Only workshop supervisors can access."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'workshop'


class IsBossOrFinance(BasePermission):
    """Boss or finance staff can access."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ('boss', 'finance')
        )
```

- [ ] **Step 11: Implement admin**

```python
# backend/apps/users/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'real_name', 'role', 'phone', 'is_active']
    list_filter = ['role', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('扩展信息', {'fields': ('real_name', 'role', 'phone')}),
    )
```

- [ ] **Step 12: Run all user tests**

```bash
cd backend
pytest apps/users/tests/ -v
```

Expected: All tests PASS

- [ ] **Step 13: Commit**

```bash
git add backend/apps/users/ backend/pytest.ini
git commit -m "feat: add User model with JWT auth (login, refresh, me)"
```

---

## Task 3: Customer Model and CRUD API

**Files:**
- Create: `backend/apps/customers/__init__.py`
- Create: `backend/apps/customers/models.py`
- Create: `backend/apps/customers/serializers.py`
- Create: `backend/apps/customers/views.py`
- Create: `backend/apps/customers/urls.py`
- Create: `backend/apps/customers/filters.py`
- Create: `backend/apps/customers/admin.py`
- Create: `backend/apps/customers/tests/__init__.py`
- Create: `backend/apps/customers/tests/test_models.py`
- Create: `backend/apps/customers/tests/test_views.py`

- [ ] **Step 1: Write Customer model test**

```python
# backend/apps/customers/tests/__init__.py
```

```python
# backend/apps/customers/tests/test_models.py
import pytest
from apps.customers.models import Customer


@pytest.mark.django_db
class TestCustomerModel:
    def test_create_customer(self):
        customer = Customer.objects.create(
            name='深圳市ABC电子有限公司',
            short_name='ABC电子',
            contact_person='张三',
            phone='13900139000',
            address='深圳市宝安区XX路XX号',
            payment_terms=30,
            default_billing_type='area',
        )
        assert customer.name == '深圳市ABC电子有限公司'
        assert customer.short_name == 'ABC电子'
        assert customer.payment_terms == 30
        assert customer.default_billing_type == 'area'
        assert customer.is_active is True
        assert str(customer) == 'ABC电子'

    def test_soft_delete(self):
        customer = Customer.objects.create(
            name='测试公司',
            short_name='测试',
        )
        customer.is_active = False
        customer.save()
        assert Customer.objects.filter(is_active=True).count() == 0
        assert Customer.objects.count() == 1
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd backend
pytest apps/customers/tests/test_models.py -v
```

Expected: FAIL - module not found

- [ ] **Step 3: Implement Customer model**

```python
# backend/apps/customers/__init__.py
```

```python
# backend/apps/customers/models.py
from django.db import models


class Customer(models.Model):
    BILLING_TYPE_CHOICES = [
        ('area', '按面积(dm²)'),
        ('weight', '按重量(kg)'),
        ('piece', '按件数'),
    ]

    name = models.CharField('公司名称', max_length=100)
    short_name = models.CharField('简称', max_length=20, blank=True)
    contact_person = models.CharField('联系人', max_length=20, blank=True)
    phone = models.CharField('电话', max_length=20, blank=True)
    address = models.CharField('地址', max_length=200, blank=True)
    payment_terms = models.IntegerField('月结天数', default=30, help_text='如30/60/90')
    default_billing_type = models.CharField(
        '默认计费方式',
        max_length=10,
        choices=BILLING_TYPE_CHOICES,
        default='area',
    )
    remark = models.TextField('备注', blank=True)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'customers'
        verbose_name = '客户'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.short_name or self.name
```

- [ ] **Step 4: Create migration and run model test**

```bash
cd backend
python manage.py makemigrations customers
python manage.py migrate
pytest apps/customers/tests/test_models.py -v
```

Expected: All tests PASS

- [ ] **Step 5: Write Customer API view tests**

```python
# backend/apps/customers/tests/test_views.py
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.customers.models import Customer

User = get_user_model()


@pytest.fixture
def finance_user(db):
    return User.objects.create_user(
        username='finance1',
        password='pass123',
        role='finance',
        real_name='财务员',
    )


@pytest.fixture
def workshop_user(db):
    return User.objects.create_user(
        username='workshop1',
        password='pass123',
        role='workshop',
        real_name='车间主管',
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
```

- [ ] **Step 6: Run tests to verify they fail**

```bash
cd backend
pytest apps/customers/tests/test_views.py -v
```

Expected: FAIL - views/urls not defined

- [ ] **Step 7: Implement serializers**

```python
# backend/apps/customers/serializers.py
from rest_framework import serializers

from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'short_name', 'contact_person', 'phone',
            'address', 'payment_terms', 'default_billing_type',
            'remark', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CustomerListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views."""
    class Meta:
        model = Customer
        fields = [
            'id', 'name', 'short_name', 'contact_person', 'phone',
            'payment_terms', 'default_billing_type', 'is_active',
        ]
```

- [ ] **Step 8: Implement filters**

```python
# backend/apps/customers/filters.py
import django_filters

from .models import Customer


class CustomerFilter(django_filters.FilterSet):
    billing_type = django_filters.ChoiceFilter(
        field_name='default_billing_type',
        choices=Customer.BILLING_TYPE_CHOICES,
    )
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Customer
        fields = ['default_billing_type', 'is_active']
```

- [ ] **Step 9: Implement views**

```python
# backend/apps/customers/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response

from apps.users.permissions import IsBossOrFinance

from .filters import CustomerFilter
from .models import Customer
from .serializers import CustomerListSerializer, CustomerSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    filterset_class = CustomerFilter
    search_fields = ['name', 'short_name', 'contact_person', 'phone']
    ordering_fields = ['name', 'created_at', 'payment_terms']

    def get_serializer_class(self):
        if self.action == 'list':
            return CustomerListSerializer
        return CustomerSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsBossOrFinance()]
        return super().get_permissions()

    def get_queryset(self):
        """Only show active customers by default."""
        qs = super().get_queryset()
        if self.action == 'list' and 'is_active' not in self.request.query_params:
            qs = qs.filter(is_active=True)
        return qs

    def destroy(self, request, *args, **kwargs):
        """Soft delete: set is_active=False instead of deleting."""
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=['is_active'])
        return Response(status=status.HTTP_204_NO_CONTENT)
```

- [ ] **Step 10: Implement URLs**

```python
# backend/apps/customers/urls.py
from rest_framework.routers import DefaultRouter

from .views import CustomerViewSet

router = DefaultRouter()
router.register('', CustomerViewSet, basename='customer')

urlpatterns = router.urls
```

- [ ] **Step 11: Implement admin**

```python
# backend/apps/customers/admin.py
from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name', 'contact_person', 'phone', 'payment_terms', 'is_active']
    list_filter = ['is_active', 'default_billing_type', 'payment_terms']
    search_fields = ['name', 'short_name', 'contact_person']
```

- [ ] **Step 12: Run all customer tests**

```bash
cd backend
pytest apps/customers/tests/ -v
```

Expected: All tests PASS

- [ ] **Step 13: Run full backend test suite**

```bash
cd backend
pytest -v
```

Expected: All tests PASS

- [ ] **Step 14: Commit**

```bash
git add backend/apps/customers/
git commit -m "feat: add Customer model with CRUD API, filters, and permissions"
```

---

## Task 4: Frontend Project Scaffolding

**Files:**
- Create: `frontend/index.html`
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`

- [ ] **Step 1: Create frontend with Vite**

```bash
mkdir -p frontend/src
```

```json
// frontend/package.json
{
  "name": "electroplating-erp-frontend",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.5.13",
    "vue-router": "^4.5.0",
    "pinia": "^2.3.0",
    "axios": "^1.7.9",
    "element-plus": "^2.9.1",
    "@element-plus/icons-vue": "^2.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.2.1",
    "vite": "^6.0.0"
  }
}
```

- [ ] **Step 2: Create vite.config.js**

```javascript
// frontend/vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: {
      '@': '/src',
    },
  },
})
```

- [ ] **Step 3: Create index.html**

```html
<!-- frontend/index.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>电镀工厂 ERP 财务系统</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
```

- [ ] **Step 4: Create main.js**

```javascript
// frontend/src/main.js
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })
app.mount('#app')
```

- [ ] **Step 5: Create App.vue**

```vue
<!-- frontend/src/App.vue -->
<template>
  <router-view />
</template>

<script setup>
</script>

<style>
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
</style>
```

- [ ] **Step 6: Install dependencies and verify it starts**

```bash
cd frontend
npm install
npm run build
```

Expected: Build succeeds (will have warnings about missing router, that's OK for now)

- [ ] **Step 7: Commit**

```bash
git add frontend/
git commit -m "feat: scaffold Vue 3 frontend with Vite, Element Plus, Pinia"
```

---

## Task 5: Frontend API Layer and Auth Store

**Files:**
- Create: `frontend/src/api/index.js`
- Create: `frontend/src/api/auth.js`
- Create: `frontend/src/api/customers.js`
- Create: `frontend/src/stores/auth.js`
- Create: `frontend/src/stores/customers.js`

- [ ] **Step 1: Create Axios instance with interceptors**

```javascript
// frontend/src/api/index.js
import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
})

// Request interceptor: attach token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor: handle 401, show errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')

      if (refreshToken) {
        try {
          const { data } = await axios.post('/api/v1/auth/refresh/', {
            refresh: refreshToken,
          })
          localStorage.setItem('access_token', data.access)
          originalRequest.headers.Authorization = `Bearer ${data.access}`
          return api(originalRequest)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      } else {
        window.location.href = '/login'
      }
    }

    const message = error.response?.data?.detail || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default api
```

- [ ] **Step 2: Create auth API module**

```javascript
// frontend/src/api/auth.js
import api from './index'

export function login(username, password) {
  return api.post('/auth/login/', { username, password })
}

export function refreshToken(refresh) {
  return api.post('/auth/refresh/', { refresh })
}

export function getMe() {
  return api.get('/auth/me/')
}
```

- [ ] **Step 3: Create customers API module**

```javascript
// frontend/src/api/customers.js
import api from './index'

export function getCustomers(params) {
  return api.get('/customers/', { params })
}

export function getCustomer(id) {
  return api.get(`/customers/${id}/`)
}

export function createCustomer(data) {
  return api.post('/customers/', data)
}

export function updateCustomer(id, data) {
  return api.put(`/customers/${id}/`, data)
}

export function deleteCustomer(id) {
  return api.delete(`/customers/${id}/`)
}
```

- [ ] **Step 4: Create auth store**

```javascript
// frontend/src/stores/auth.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getMe } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token') || '')

  const isLoggedIn = computed(() => !!accessToken.value)
  const userRole = computed(() => user.value?.role || '')

  async function login(username, password) {
    const { data } = await loginApi(username, password)
    accessToken.value = data.access
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    user.value = data.user
  }

  async function fetchUser() {
    try {
      const { data } = await getMe()
      user.value = data
    } catch {
      logout()
    }
  }

  function logout() {
    user.value = null
    accessToken.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return { user, accessToken, isLoggedIn, userRole, login, fetchUser, logout }
})
```

- [ ] **Step 5: Create customers store**

```javascript
// frontend/src/stores/customers.js
import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getCustomers,
  createCustomer,
  updateCustomer,
  deleteCustomer,
} from '@/api/customers'

export const useCustomerStore = defineStore('customers', () => {
  const customers = ref([])
  const total = ref(0)
  const loading = ref(false)

  async function fetchCustomers(params = {}) {
    loading.value = true
    try {
      const { data } = await getCustomers(params)
      customers.value = data.results
      total.value = data.count
    } finally {
      loading.value = false
    }
  }

  async function addCustomer(data) {
    const { data: newCustomer } = await createCustomer(data)
    return newCustomer
  }

  async function editCustomer(id, data) {
    const { data: updated } = await updateCustomer(id, data)
    return updated
  }

  async function removeCustomer(id) {
    await deleteCustomer(id)
  }

  return { customers, total, loading, fetchCustomers, addCustomer, editCustomer, removeCustomer }
})
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/api/ frontend/src/stores/
git commit -m "feat: add API layer (axios + interceptors) and Pinia stores for auth/customers"
```

---

## Task 6: Frontend Router and Layout

**Files:**
- Create: `frontend/src/router/index.js`
- Create: `frontend/src/views/Login.vue`
- Create: `frontend/src/views/Layout.vue`
- Create: `frontend/src/views/Dashboard.vue`

- [ ] **Step 1: Create router with guards**

```javascript
// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '经营看板' },
      },
      {
        path: 'customers',
        name: 'Customers',
        component: () => import('@/views/customers/CustomerList.vue'),
        meta: { title: '客户管理' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth === false) {
    if (auth.isLoggedIn) {
      next('/')
    } else {
      next()
    }
    return
  }

  if (!auth.isLoggedIn) {
    next('/login')
    return
  }

  if (!auth.user) {
    await auth.fetchUser()
  }

  next()
})

export default router
```

- [ ] **Step 2: Create Login page**

```vue
<!-- frontend/src/views/Login.vue -->
<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2 class="login-title">电镀工厂 ERP 财务系统</h2>
      </template>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="0"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="用户名"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await auth.login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    // Error already handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
}
.login-card {
  width: 400px;
}
.login-title {
  text-align: center;
  margin: 0;
  font-size: 20px;
  color: #303133;
}
.login-btn {
  width: 100%;
}
</style>
```

- [ ] **Step 3: Create Layout with sidebar**

```vue
<!-- frontend/src/views/Layout.vue -->
<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="layout-aside">
      <div class="logo">
        <span v-if="!isCollapse">电镀 ERP</span>
        <span v-else>ERP</span>
      </div>
      <el-menu
        :default-active="$route.path"
        :collapse="isCollapse"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item index="/">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>经营看板</template>
        </el-menu-item>
        <el-menu-item index="/customers">
          <el-icon><User /></el-icon>
          <template #title>客户管理</template>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="layout-header">
        <el-icon
          class="collapse-btn"
          @click="isCollapse = !isCollapse"
        >
          <Fold v-if="!isCollapse" />
          <Expand v-else />
        </el-icon>
        <div class="header-right">
          <span class="user-name">{{ auth.user?.real_name }}</span>
          <el-dropdown @command="handleCommand">
            <el-avatar :size="32">
              {{ auth.user?.real_name?.charAt(0) }}
            </el-avatar>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { DataAnalysis, User, Fold, Expand } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const isCollapse = ref(false)

function handleCommand(command) {
  if (command === 'logout') {
    auth.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}
.layout-aside {
  background: #304156;
  transition: width 0.3s;
  overflow: hidden;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid #3d4d5e;
}
.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #e6e6e6;
  background: #fff;
}
.collapse-btn {
  font-size: 20px;
  cursor: pointer;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.user-name {
  font-size: 14px;
  color: #606266;
}
.layout-main {
  background: #f0f2f5;
}
</style>
```

- [ ] **Step 4: Create placeholder Dashboard**

```vue
<!-- frontend/src/views/Dashboard.vue -->
<template>
  <div class="dashboard">
    <h2>经营看板</h2>
    <p>（将在后续阶段实现完整看板功能）</p>
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="本月收入" value="0" prefix="¥" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="本月支出" value="0" prefix="¥" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="本月利润" value="0" prefix="¥" />
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="应收余额" value="0" prefix="¥" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
</script>

<style scoped>
.dashboard h2 {
  margin-top: 0;
}
</style>
```

- [ ] **Step 5: Verify frontend builds**

```bash
cd frontend
npm run build
```

Expected: Build succeeds

- [ ] **Step 6: Commit**

```bash
git add frontend/src/router/ frontend/src/views/
git commit -m "feat: add router with auth guards, Login page, Layout with sidebar, Dashboard placeholder"
```

---

## Task 7: Customer Management Pages

**Files:**
- Create: `frontend/src/views/customers/CustomerList.vue`
- Create: `frontend/src/views/customers/CustomerForm.vue`
- Create: `frontend/src/utils/format.js`

- [ ] **Step 1: Create format utilities**

```javascript
// frontend/src/utils/format.js
/**
 * Format a number as CNY currency.
 * @param {number} value
 * @returns {string}
 */
export function formatCurrency(value) {
  if (value == null) return '¥0.00'
  return `¥${Number(value).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`
}

/**
 * Format ISO date string to YYYY-MM-DD.
 * @param {string} dateStr
 * @returns {string}
 */
export function formatDate(dateStr) {
  if (!dateStr) return '-'
  return dateStr.slice(0, 10)
}

/**
 * Map billing type code to label.
 */
export const billingTypeMap = {
  area: '按面积(dm²)',
  weight: '按重量(kg)',
  piece: '按件数',
}
```

- [ ] **Step 2: Create CustomerForm dialog component**

```vue
<!-- frontend/src/views/customers/CustomerForm.vue -->
<template>
  <el-dialog
    :title="isEdit ? '编辑客户' : '新增客户'"
    :model-value="visible"
    width="600px"
    @close="$emit('update:visible', false)"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="公司名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入完整公司名称" />
      </el-form-item>
      <el-form-item label="简称" prop="short_name">
        <el-input v-model="form.short_name" placeholder="如: ABC电子" />
      </el-form-item>
      <el-form-item label="联系人" prop="contact_person">
        <el-input v-model="form.contact_person" />
      </el-form-item>
      <el-form-item label="电话" prop="phone">
        <el-input v-model="form.phone" />
      </el-form-item>
      <el-form-item label="地址">
        <el-input v-model="form.address" />
      </el-form-item>
      <el-form-item label="月结天数" prop="payment_terms">
        <el-select v-model="form.payment_terms" style="width: 100%">
          <el-option :value="30" label="30天" />
          <el-option :value="60" label="60天" />
          <el-option :value="90" label="90天" />
        </el-select>
      </el-form-item>
      <el-form-item label="计费方式" prop="default_billing_type">
        <el-select v-model="form.default_billing_type" style="width: 100%">
          <el-option value="area" label="按面积(dm²)" />
          <el-option value="weight" label="按重量(kg)" />
          <el-option value="piece" label="按件数" />
        </el-select>
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.remark" type="textarea" :rows="3" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="handleSubmit">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useCustomerStore } from '@/stores/customers'

const props = defineProps({
  visible: Boolean,
  customer: { type: Object, default: null },
})

const emit = defineEmits(['update:visible', 'saved'])

const isEdit = ref(false)
const formRef = ref(null)
const submitting = ref(false)
const store = useCustomerStore()

const form = reactive({
  name: '',
  short_name: '',
  contact_person: '',
  phone: '',
  address: '',
  payment_terms: 30,
  default_billing_type: 'area',
  remark: '',
})

const rules = {
  name: [{ required: true, message: '请输入公司名称', trigger: 'blur' }],
  payment_terms: [{ required: true, message: '请选择月结天数', trigger: 'change' }],
  default_billing_type: [{ required: true, message: '请选择计费方式', trigger: 'change' }],
}

watch(() => props.customer, (val) => {
  if (val) {
    isEdit.value = true
    Object.assign(form, val)
  } else {
    isEdit.value = false
    Object.assign(form, {
      name: '', short_name: '', contact_person: '', phone: '',
      address: '', payment_terms: 30, default_billing_type: 'area', remark: '',
    })
  }
}, { immediate: true })

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (isEdit.value) {
      await store.editCustomer(props.customer.id, form)
      ElMessage.success('更新成功')
    } else {
      await store.addCustomer(form)
      ElMessage.success('创建成功')
    }
    emit('update:visible', false)
    emit('saved')
  } catch {
    // Handled by interceptor
  } finally {
    submitting.value = false
  }
}
</script>
```

- [ ] **Step 3: Create CustomerList page**

```vue
<!-- frontend/src/views/customers/CustomerList.vue -->
<template>
  <div class="customer-list">
    <div class="page-header">
      <h2>客户管理</h2>
      <el-button type="primary" @click="handleAdd">新增客户</el-button>
    </div>

    <el-card>
      <div class="filter-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索客户名称/联系人/电话"
          clearable
          style="width: 300px"
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button @click="handleSearch">搜索</el-button>
          </template>
        </el-input>
        <el-select
          v-model="billingFilter"
          placeholder="计费方式"
          clearable
          style="width: 150px; margin-left: 12px"
          @change="handleSearch"
        >
          <el-option value="area" label="按面积" />
          <el-option value="weight" label="按重量" />
          <el-option value="piece" label="按件数" />
        </el-select>
      </div>

      <el-table
        v-loading="store.loading"
        :data="store.customers"
        stripe
        style="width: 100%; margin-top: 16px"
      >
        <el-table-column prop="short_name" label="简称" width="120" />
        <el-table-column prop="name" label="公司名称" min-width="200" />
        <el-table-column prop="contact_person" label="联系人" width="100" />
        <el-table-column prop="phone" label="电话" width="140" />
        <el-table-column prop="payment_terms" label="月结天数" width="100" align="center">
          <template #default="{ row }">{{ row.payment_terms }}天</template>
        </el-table-column>
        <el-table-column prop="default_billing_type" label="计费方式" width="120">
          <template #default="{ row }">
            {{ billingTypeMap[row.default_billing_type] }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleEdit(row)">编辑</el-button>
            <el-popconfirm
              title="确认删除该客户？"
              @confirm="handleDelete(row)"
            >
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-if="store.total > 20"
        class="pagination"
        layout="total, prev, pager, next"
        :total="store.total"
        :page-size="20"
        :current-page="currentPage"
        @current-change="handlePageChange"
      />
    </el-card>

    <CustomerForm
      v-model:visible="formVisible"
      :customer="editingCustomer"
      @saved="loadData"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useCustomerStore } from '@/stores/customers'
import { billingTypeMap } from '@/utils/format'
import CustomerForm from './CustomerForm.vue'

const store = useCustomerStore()
const searchQuery = ref('')
const billingFilter = ref('')
const currentPage = ref(1)
const formVisible = ref(false)
const editingCustomer = ref(null)

function loadData() {
  const params = { page: currentPage.value }
  if (searchQuery.value) params.search = searchQuery.value
  if (billingFilter.value) params.default_billing_type = billingFilter.value
  store.fetchCustomers(params)
}

function handleSearch() {
  currentPage.value = 1
  loadData()
}

function handlePageChange(page) {
  currentPage.value = page
  loadData()
}

function handleAdd() {
  editingCustomer.value = null
  formVisible.value = true
}

function handleEdit(row) {
  editingCustomer.value = { ...row }
  formVisible.value = true
}

async function handleDelete(row) {
  await store.removeCustomer(row.id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.page-header h2 {
  margin: 0;
}
.filter-bar {
  display: flex;
  align-items: center;
}
.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}
</style>
```

- [ ] **Step 4: Verify frontend builds**

```bash
cd frontend
npm run build
```

Expected: Build succeeds

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/customers/ frontend/src/utils/
git commit -m "feat: add customer list and form pages with search, filter, CRUD"
```

---

## Task 8: End-to-End Verification

**Files:** None new — integration test of existing code.

- [ ] **Step 1: Create superuser for testing**

```bash
cd backend
python manage.py createsuperuser --username admin --email admin@test.com
# Enter password when prompted: admin123
```

- [ ] **Step 2: Start backend server**

```bash
cd backend
python manage.py runserver 0.0.0.0:8000
```

- [ ] **Step 3: Test auth API manually**

```bash
# In a new terminal
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Expected: JSON with `access`, `refresh`, `user` fields

- [ ] **Step 4: Test customer API manually**

```bash
# Use token from previous step
TOKEN="<paste access token>"

# Create customer
curl -X POST http://localhost:8000/api/v1/customers/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name":"测试公司","short_name":"测试","payment_terms":30,"default_billing_type":"area"}'

# List customers
curl http://localhost:8000/api/v1/customers/ \
  -H "Authorization: Bearer $TOKEN"
```

Expected: Customer created and listed successfully

- [ ] **Step 5: Start frontend dev server**

```bash
cd frontend
npm run dev
```

Open browser to `http://localhost:3000` — should see login page, be able to log in, see sidebar, navigate to customer list.

- [ ] **Step 6: Run full test suite**

```bash
cd backend
pytest -v
```

Expected: All tests PASS

- [ ] **Step 7: Final commit for Phase 1**

```bash
git add -A
git commit -m "feat: Phase 1 complete - project setup, auth, customer management"
```

---

## Summary

Phase 1 establishes:
- **Backend**: Django project with split settings, JWT auth, User model with roles, Customer CRUD with permissions
- **Frontend**: Vue 3 app with Element Plus, login flow, sidebar layout, customer management pages
- **Testing**: pytest with django_db marker, model + view tests for both apps

**Next phase:** Phase 2 will add PlatingProcess/PricingRule models and full Order management (model, API, frontend pages).
