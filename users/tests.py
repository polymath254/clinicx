import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User

@pytest.mark.django_db
class TestUserAPI:
    @pytest.fixture
    def user(self):
        return User.objects.create_user(
            username="janedoe",
            email="jane@example.com",
            password="SafePass123",
            role="patient"
        )

    @pytest.fixture
    def client(self):
        return APIClient()

    @pytest.fixture
    def auth_client(self, user):
        client = APIClient()
        # Obtain JWT (assuming you use simplejwt)
        response = client.post(
            reverse("token_obtain_pair"),
            {"email": "jane@example.com", "password": "SafePass123"}
        )
        assert response.status_code == 200
        access = response.data["access"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        return client

    def test_profile_view_authenticated(self, auth_client):
        response = auth_client.get(reverse("user-profile"))
        assert response.status_code == 200
        assert response.data["email"] == "jane@example.com"
        assert response.data["username"] == "janedoe"

    def test_profile_view_unauthenticated(self, client):
        response = client.get(reverse("user-profile"))
        assert response.status_code == 401  # Unauthorized

    def test_profile_edit(self, auth_client):
        payload = {"username": "janedoe2", "phone_number": "+254700000001"}
        response = auth_client.patch(reverse("user-profile"), payload)
        assert response.status_code == 200
        assert response.data["username"] == "janedoe2"

    def test_invalid_patch_data(self, auth_client):
        payload = {"username": ""}  # Empty username, should fail
        response = auth_client.patch(reverse("user-profile"), payload)
        assert response.status_code == 400

    def test_user_cannot_change_role(self, auth_client):
        payload = {"role": "admin"}
        response = auth_client.patch(reverse("user-profile"), payload)
        # Role should not change (read_only)
        assert response.status_code == 200
        assert response.data["role"] == "patient"

    def test_create_user_directly(self, db):
        user = User.objects.create_user(
            username="newuser",
            email="newuser@example.com",
            password="SuperPass456",
            role="doctor"
        )
        assert user.email == "newuser@example.com"
        assert user.check_password("SuperPass456")
        assert user.role == "doctor"

    def test_create_superuser(self, db):
        user = User.objects.create_superuser(
            username="admin",
            email="admin@clinicx.com",
            password="AdminPass789"
        )
        assert user.is_staff
        assert user.is_superuser

    def test_duplicate_email(self, db):
        User.objects.create_user(
            username="uniqueuser1",
            email="unique@example.com",
            password="pass1"
        )
        with pytest.raises(Exception):
            User.objects.create_user(
                username="uniqueuser2",
                email="unique@example.com",  # Duplicate email
                password="pass2"
            )
    def test_duplicate_username(self, db):
    # Create the initial user
     User.objects.create_user(
        username="uniqueuser",
        email="unique1@example.com",
        password="pass1"
    )
    # Try to create another user with the same username
    with pytest.raises(Exception) as excinfo:
        User.objects.create_user(
            username="uniqueuser",  # Duplicate username
            email="unique2@example.com",
            password="pass2"
        )
    # Optional: Check the error message for clarity
    assert "UNIQUE constraint" in str(excinfo.value) or "unique" in str(excinfo.value).lower()


