
from rest_framework.routers import DefaultRouter
from .views import SupplierViewSet, DrugViewSet, PurchaseOrderViewSet

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'drugs',      DrugViewSet,      basename='drug')
router.register(r'purchase-orders', PurchaseOrderViewSet, basename='purchaseorder')

urlpatterns = router.urls
