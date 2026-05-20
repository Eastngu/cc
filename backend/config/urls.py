from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/customers/', include('apps.customers.urls')),
    path('api/v1/', include('apps.processes.urls')),
    path('api/v1/orders/', include('apps.orders.urls')),
    path('api/v1/', include('apps.finance.urls')),
    path('api/v1/costing/', include('apps.costing.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
]
