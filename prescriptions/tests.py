import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from .models import Prescription, PrescriptionDrug
from inventory.models import Drug

User = get_user_model()

@pytest.mark.django_db
class TestPrescriptionAPI:
    @pytest.fixture
    def doctor(self):
        return User.objects.create_user(
            username='doc', email='doc@example.com',
            password='DocPass1!', role='doctor'
        )

    @pytest.fixture
    def patient(self):
        return User.objects.create_user(
            username='pat', email='pat@example.com',
            password='PatPass1!', role='patient'
        )

    @pytest.fixture
    def pharmacist(self):
        return User.objects.create_user(
            username='pharm', email='pharm@example.com',
            password='PharmPass1!', role='pharmacist'
        )

    @pytest.fixture
    def admin(self):
        return User.objects.create_superuser(
            username='adm', email='adm@example.com',
            password='AdmPass1!'
        )

    @pytest.fixture
    def drug(self):
        return Drug.objects.create(name='Aspirin', description='Painkiller', price=1.0, quantity=100, reorder_threshold=10, supplier_id=1)

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
    def prescription_data(self, doctor, patient, drug):
        return {
            'doctor': doctor.id,
            'patient': patient.id,
            'notes': 'Take after meals.',
            'drugs': [
                {'drug': drug.id, 'dosage': '100mg', 'quantity': 10}
            ]
        }

    def test_doctor_can_create(self, client_for, doctor, patient, drug, prescription_data):
        client = client_for(doctor)
        resp = client.post(reverse('prescription-list'), prescription_data, format='json')
        assert resp.status_code == 201
        assert Prescription.objects.count() == 1
        assert PrescriptionDrug.objects.count() == 1

    def test_patient_cannot_create(self, client_for, patient, prescription_data):
        client = client_for(patient)
        resp = client.post(reverse('prescription-list'), prescription_data, format='json')
        assert resp.status_code == 403

    def test_nested_validation(self, client_for, doctor, patient, prescription_data):
        # invalid drug quantity
        prescription_data['drugs'][0]['quantity'] = -5
        client = client_for(doctor)
        resp = client.post(reverse('prescription-list'), prescription_data, format='json')
        assert resp.status_code == 400

    def test_patient_can_view_their(self, client_for, doctor, patient, prescription_data):
        # create as doctor
        Prescription.objects.create(doctor=doctor, patient=patient)
        client = client_for(patient)
        resp = client.get(reverse('prescription-list'))
        assert resp.status_code == 200

    def test_pharmacist_can_view_all(self, client_for, pharmacist, doctor, patient):
        Prescription.objects.create(doctor=doctor, patient=patient)
        client = client_for(pharmacist)
        resp = client.get(reverse('prescription-list'))
        assert resp.status_code == 200
        assert len(resp.data) >= 1

    def test_admin_can_delete(self, client_for, admin, doctor, patient):
        p = Prescription.objects.create(doctor=doctor, patient=patient)
        client = client_for(admin)
        resp = client.delete(reverse('prescription-detail', args=[p.id]))
        assert resp.status_code == 204

    def test_forbid_other_doctor(self, client_for, doctor, patient, drug):
        other_doc = User.objects.create_user(username='doc2', email='doc2@example.com', password='Doc2Pass!', role='doctor')
        Presc = Prescription.objects.create(doctor=other_doc, patient=patient)
        client = client_for(doctor)
        resp = client.get(reverse('prescription-detail', args=[Presc.id]))
        assert resp.status_code in (403, 404)

    def test_unauthenticated_forbidden(self):
        assert APIClient().get(reverse('prescription-list')).status_code == 401
    def test_prescription_drug_serializer(self, prescription_data):
        # Test the PrescriptionDrugSerializer directly
        from .serializers import PrescriptionDrugSerializer
        serializer = PrescriptionDrugSerializer(data=prescription_data['drugs'][0])
        assert serializer.is_valid()
        assert serializer.validated_data['drug'].id == prescription_data['drugs'][0]['drug']
        assert serializer.validated_data['dosage'] == prescription_data['drugs'][0]['dosage']
        assert serializer.validated_data['quantity'] == prescription_data['drugs'][0]['quantity']