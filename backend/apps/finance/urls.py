from rest_framework.routers import DefaultRouter
from .views import ReceivableViewSet, PayableViewSet, PaymentViewSet

router = DefaultRouter()
router.register('receivables', ReceivableViewSet, basename='receivable')
router.register('payables', PayableViewSet, basename='payable')
router.register('payments', PaymentViewSet, basename='payment')
urlpatterns = router.urls
