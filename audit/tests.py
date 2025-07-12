import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from patients.models import PatientProfile
from users.models import User
from audit.models import AuditLog

User = get_user_model()

@pytest.mark.django_db
class TestAuditLog:
    @pytest.fixture
    def patient(self):
        return User.objects.create_user(
            username='pat', email='pat@example.com',
            password='PatPass1!', role='patient'
        )

    @pytest.fixture
    def client_for(self):
        def _make(user):
            client = APIClient()
            tok = client.post(reverse('token_obtain_pair'),
                              {'email': user.email,'password': user.password})
            client.credentials(HTTP_AUTHORIZATION=f"Bearer {tok.data['access']}")
            return client
        return _make

    def test_create_patient_generates_audit(self, patient):
        # Creating PatientProfile triggers audit entry
        pp = PatientProfile.objects.create(user=patient, allergies='None')
        logs = AuditLog.objects.filter(
            content_type__model='patientprofile',
            object_id=str(pp.pk),
            action=AuditLog.ACTION_CREATE
        )
        assert logs.exists()

    def test_update_patient_generates_audit(self, patient):
        pp = PatientProfile.objects.create(user=patient)
        pp.allergies = 'Pollen'
        pp.save()
        logs = AuditLog.objects.filter(
            content_type__model='patientprofile',
            object_id=str(pp.pk),
            action=AuditLog.ACTION_UPDATE
        )
        assert logs.exists()

    def test_delete_patient_generates_audit(self, patient):
        pp = PatientProfile.objects.create(user=patient)
        pk = pp.pk
        pp.delete()
        logs = AuditLog.objects.filter(
            content_type__model='patientprofile',
            object_id=str(pk),
            action=AuditLog.ACTION_DELETE
        )
        assert logs.exists()

    def test_api_read_requires_auth(self):
        client = APIClient()
        assert client.get(reverse('audit-log-list')).status_code == 401

    def test_api_read_allows_authenticated(self, client_for, patient):
        client = client_for(patient)
        assert client.get(reverse('audit-log-list')).status_code == 200

    def test_filter_by_action(self, client_for, patient):
        pp = PatientProfile.objects.create(user=patient)
        client = client_for(patient)
        resp = client.get(reverse('audit-log-list'), {'action': 'create'})
        assert resp.status_code == 200
        assert all(entry['action'] == 'create' for entry in resp.data)
