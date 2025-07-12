from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = router.urls
