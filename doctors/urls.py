from rest_framework.routers import DefaultRouter
from .views import DoctorProfileViewSet

router = DefaultRouter()
router.register(r'', DoctorProfileViewSet, basename='doctor-profile')

urlpatterns = router.urls
