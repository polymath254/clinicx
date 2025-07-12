from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Admins see all users; regular users see only their own data
        if user.is_superuser or getattr(user, "role", None) == "admin":
            return User.objects.all()
        return User.objects.filter(pk=user.pk)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='register', permission_classes=[permissions.AllowAny])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Automatically issue JWT tokens on registration
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": self.get_serializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }, status=status.HTTP_201_CREATED)

    # Optionally: endpoint for admins to activate/deactivate or change roles

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='activate')
    def activate_user(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({"status": "user activated"})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser], url_path='deactivate')
    def deactivate_user(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({"status": "user deactivated"})


