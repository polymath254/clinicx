import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from patients.models import PatientProfile

User = get_user_model()

@pytest.mark.django_db
class TestPatientProfileAPI:
    @pytest.fixture
    def patient_user(self):
        user = User.objects.create_user(
            username="testpatient",
            email="patient@example.com",
            password="PatientPass123!",
            role="patient"
        )
        # Profile should be auto-created by signal
        return user

    @pytest.fixture
    def admin_user(self):
        return User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="AdminPass123!"
        )

    @pytest.fixture
    def auth_client(self, patient_user):
        client = APIClient()
        response = client.post(
            reverse("token_obtain_pair"),
            {"email": "patient@example.com", "password": "PatientPass123!"}
        )
        assert response.status_code == 200
        access = response.data["access"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        return client

    @pytest.fixture
    def admin_client(self, admin_user):
        client = APIClient()
        response = client.post(
            reverse("token_obtain_pair"),
            {"email": "admin@example.com", "password": "AdminPass123!"}
        )
        assert response.status_code == 200
        access = response.data["access"]
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        return client

    def test_auto_profile_created(self, patient_user):
        assert hasattr(patient_user, 'patient_profile')
        assert isinstance(patient_user.patient_profile, PatientProfile)

    def test_get_own_profile(self, auth_client, patient_user):
        response = auth_client.get(reverse("patient-profile-me"))
        assert response.status_code == 200
        assert response.data["email"] == patient_user.email

    def test_update_own_profile(self, auth_client):
        response = auth_client.patch(
            reverse("patient-profile-me"),
            {"allergies": "Peanuts, Penicillin"}
        )
        assert response.status_code == 200
        assert "Peanuts" in response.data["allergies"]

    def test_forbid_other_patient_profile(self, auth_client, db):
        # Create another patient
        other_user = User.objects.create_user(
            username="anotherpatient",
            email="another@example.com",
            password="AnotherPass123!",
            role="patient"
        )
        other_profile = other_user.patient_profile
        response = auth_client.get(reverse("patient-profile-detail", args=[other_profile.id]))
        assert response.status_code in (403, 404)

    def test_admin_can_access_any_profile(self, admin_client, patient_user):
        profile = patient_user.patient_profile
        url = reverse("patient-profile-detail", args=[profile.id])
        response = admin_client.get(url)
        assert response.status_code == 200
        assert response.data["email"] == patient_user.email

    def test_profile_requires_authentication(self):
        client = APIClient()
        response = client.get(reverse("patient-profile-me"))
        assert response.status_code == 401

    def test_patch_invalid_data(self, auth_client):
        # Edge case: Patch with invalid date
        response = auth_client.patch(
            reverse("patient-profile-me"),
            {"date_of_birth": "invalid-date"}
        )
        assert response.status_code == 400

    def test_profile_not_found(self, admin_client, db):
        url = reverse("patient-profile-detail", args=[9999])
        response = admin_client.get(url)
        assert response.status_code == 404
    def test_profile_list(self, admin_client):
        response = admin_client.get(reverse("patient-profile-list"))
        assert response.status_code == 200
        assert isinstance(response.data, list)