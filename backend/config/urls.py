from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('apps.users.urls')),
    path('api/v1/customers/', include('apps.customers.urls')),
    path('api/v1/', include('apps.processes.urls')),
    path('api/v1/orders/', include('apps.orders.urls')),
    path('api/v1/', include('apps.finance.urls')),
    path('api/v1/costing/', include('apps.costing.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    # Serve Vue frontend for all non-API routes
    re_path(r'^(?!api/|admin/|assets/).*$', TemplateView.as_view(template_name='index.html')),
]
