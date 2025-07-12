from rest_framework.routers import DefaultRouter
from .views import NotificationLogViewSet

router = DefaultRouter()
router.register(r'logs', NotificationLogViewSet, basename='notification-log')

urlpatterns = router.urls
