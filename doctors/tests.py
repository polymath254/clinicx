import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import DoctorProfile

User = get_user_model()

@pytest.mark.django_db
class TestDoctorProfileAPI:
    @pytest.fixture
    def doctor_user(self):
        return User.objects.create_user(
            username='doc1',
            email='doc1@example.com',
            password='DoctorPass123!',
            role='doctor'
        )

    @pytest.fixture
    def admin_user(self):
        return User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='AdminPass123!'
        )

    @pytest.fixture
    def patient_user(self):
        return User.objects.create_user(
            username='pat1',
            email='pat1@example.com',
            password='PatientPass123!',
            role='patient'
        )

    @pytest.fixture
    def doctor_client(self, doctor_user):
        client = APIClient()
        resp = client.post(
            reverse('token_obtain_pair'),
            {'email': doctor_user.email, 'password': 'DoctorPass123!'}
        )
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
        return client

    @pytest.fixture
    def admin_client(self, admin_user):
        client = APIClient()
        resp = client.post(
            reverse('token_obtain_pair'),
            {'email': admin_user.email, 'password': 'AdminPass123!'}
        )
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
        return client

    @pytest.fixture
    def patient_client(self, patient_user):
        client = APIClient()
        resp = client.post(
            reverse('token_obtain_pair'),
            {'email': patient_user.email, 'password': 'PatientPass123!'}
        )
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
        return client

    def test_auto_profile_created(self, doctor_user):
        assert hasattr(doctor_user, 'doctor_profile')
        assert isinstance(doctor_user.doctor_profile, DoctorProfile)

    def test_doctor_can_view_own_profile(self, doctor_client):
        url = reverse('doctor-profile-me')
        resp = doctor_client.get(url)
        assert resp.status_code == 200
        assert resp.data['email'] == 'doc1@example.com'

    def test_doctor_can_update_own_profile(self, doctor_client):
        url = reverse('doctor-profile-me')
        resp = doctor_client.patch(url, {'specialty': 'Neurology'})
        assert resp.status_code == 200
        assert resp.data['specialty'] == 'Neurology'

    def test_doctor_cannot_update_other(self, doctor_client, admin_user):
        other = User.objects.create_user(
            username='doc2',
            email='doc2@example.com',
            password='DoctorPass456!',
            role='doctor'
        )
        url = reverse('doctor-profile-detail', args=[other.doctor_profile.id])
        resp = doctor_client.patch(url, {'specialty': 'Dermatology'})
        assert resp.status_code == 403

    def test_patient_can_list_and_retrieve(self, patient_client, doctor_user):
        list_url = reverse('doctor-profile-list')
        resp = patient_client.get(list_url)
        assert resp.status_code == 200
        detail_url = reverse('doctor-profile-detail', args=[doctor_user.doctor_profile.id])
        resp2 = patient_client.get(detail_url)
        assert resp2.status_code == 200

    def test_unauthenticated_forbidden(self):
        client = APIClient()
        assert client.get(reverse('doctor-profile-list')).status_code == 401

    def test_admin_can_list_and_update_any(self, admin_client, doctor_user):
        list_url = reverse('doctor-profile-list')
        assert admin_client.get(list_url).status_code == 200
        detail_url = reverse('doctor-profile-detail', args=[doctor_user.doctor_profile.id])
        resp = admin_client.patch(detail_url, {'specialty': 'Cardiology'})
        assert resp.status_code == 200
        assert resp.data['specialty'] == 'Cardiology'

    def test_invalid_schedule(self, admin_client, doctor_user):
        url = reverse('doctor-profile-me')
        resp = admin_client.patch(url, {'schedule': 'not valid json'})
        assert resp.status_code == 400
