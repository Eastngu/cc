from rest_framework.routers import DefaultRouter
from .views import OrderCostViewSet

router = DefaultRouter()
router.register('', OrderCostViewSet, basename='order-cost')
urlpatterns = router.urls
