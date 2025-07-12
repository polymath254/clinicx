import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta
from .models import Appointment

User = get_user_model()

@pytest.mark.django_db
class TestAppointmentAPI:
    @pytest.fixture
    def patient(self):
        return User.objects.create_user(
            username='pat', email='pat@example.com',
            password='Pt123456!', role='patient'
        )

    @pytest.fixture
    def doctor(self):
        return User.objects.create_user(
            username='doc', email='doc@example.com',
            password='Dr123456!', role='doctor'
        )

    @pytest.fixture
    def admin(self):
        return User.objects.create_superuser(
            username='adm', email='adm@example.com',
            password='Ad123456!'
        )

    @pytest.fixture
    def client_for(self):
        def _make(user):
            client = APIClient()
            resp = client.post(
                reverse('token_obtain_pair'),
                {'email': user.email, 'password': user.password}
            )
            client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
            return client
        return _make

    @pytest.fixture
    def existing_appt(self, patient, doctor):
        return Appointment.objects.create(
            patient=patient,
            doctor=doctor,
            datetime=timezone.now() + timedelta(days=1)
        )

    def test_patient_create_future(self, client_for, patient, doctor):
        client = client_for(patient)
        url = reverse('appointment-list')
        dt = (timezone.now() + timedelta(days=2)).isoformat()
        resp = client.post(url, {'doctor': doctor.id, 'datetime': dt})
        assert resp.status_code == 201
        assert resp.data['doctor'] == doctor.id

    def test_patient_cannot_create_past(self, client_for, patient, doctor):
        client = client_for(patient)
        url = reverse('appointment-list')
        dt = (timezone.now() - timedelta(hours=1)).isoformat()
        resp = client.post(url, {'doctor': doctor.id, 'datetime': dt})
        assert resp.status_code == 400

    def test_double_booking_blocked(self, client_for, patient, doctor, existing_appt):
        client = client_for(patient)
        url = reverse('appointment-list')
        dt = existing_appt.datetime.isoformat()
        resp = client.post(url, {'doctor': doctor.id, 'datetime': dt})
        assert resp.status_code == 400

    def test_patient_list_and_me(self, client_for, patient, doctor, existing_appt):
        client = client_for(patient)
        list_resp = client.get(reverse('appointment-list'))
        assert list_resp.status_code == 200
        me_resp = client.get(reverse('appointment-me'))
        assert me_resp.status_code == 200
        assert len(me_resp.data) == 1

    def test_doctor_only_sees_own(self, client_for, patient, doctor, existing_appt):
        client = client_for(doctor)
        resp = client.get(reverse('appointment-list'))
        assert resp.status_code == 200
        assert all(a['doctor'] == doctor.id for a in resp.data)

    def test_admin_sees_all(self, client_for, patient, doctor, admin, existing_appt):
        client = client_for(admin)
        resp = client.get(reverse('appointment-list'))
        assert resp.status_code == 200
        assert len(resp.data) == Appointment.objects.count()

    def test_patient_cancel(self, client_for, patient, doctor, existing_appt):
        client = client_for(patient)
        url = reverse('appointment-detail', args=[existing_appt.id])
        resp = client.patch(url, {'status': Appointment.STATUS_CANCELLED})
        assert resp.status_code == 200
        assert resp.data['status'] == Appointment.STATUS_CANCELLED

    def test_doctor_complete(self, client_for, patient, doctor, existing_appt):
        client = client_for(doctor)
        url = reverse('appointment-detail', args=[existing_appt.id])
        resp = client.patch(url, {'status': Appointment.STATUS_COMPLETED})
        assert resp.status_code == 200
        assert resp.data['status'] == Appointment.STATUS_COMPLETED

    def test_forbid_others(self, client_for, patient, doctor, existing_appt):
        # A different patient
        other = User.objects.create_user(
            username='pat2', email='pat2@example.com',
            password='P2t23456!', role='patient'
        )
        client = client_for(other)
        url = reverse('appointment-detail', args=[existing_appt.id])
        resp = client.patch(url, {'status': Appointment.STATUS_CANCELLED})
        assert resp.status_code in (403, 404)

    def test_unauthenticated(self):
        assert APIClient().get(reverse('appointment-list')).status_code == 401
