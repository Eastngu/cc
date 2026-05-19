from rest_framework.routers import DefaultRouter
from .views import PlatingProcessViewSet, PricingRuleViewSet

router = DefaultRouter()
router.register('processes', PlatingProcessViewSet, basename='process')
router.register('pricing-rules', PricingRuleViewSet, basename='pricing-rule')
urlpatterns = router.urls
