from django.urls import path
from .views import DashboardView, RevenueTrendView, CustomerAnalysisView, CostAnalysisView

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('revenue-trend/', RevenueTrendView.as_view(), name='revenue-trend'),
    path('customer-analysis/', CustomerAnalysisView.as_view(), name='customer-analysis'),
    path('cost-analysis/', CostAnalysisView.as_view(), name='cost-analysis'),
]
