import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from inventory.models import Drug, Supplier
from prescriptions.models import Prescription, PrescriptionDrug
from .models import Order, PurchaseOrder

User = get_user_model()

@pytest.mark.django_db
class TestOrderAPI:
    @pytest.fixture
    def pharmacist(self):
        return User.objects.create_user(
            username='pharm', email='pharm@example.com',
            password='PharmPass1!', role='pharmacist'
        )
    @pytest.fixture
    def patient(self):
        return User.objects.create_user(
            username='pat', email='pat@example.com',
            password='PatPass1!', role='patient'
        )
    @pytest.fixture
    def doctor(self):
        return User.objects.create_user(
            username='doc', email='doc@example.com',
            password='DocPass1!', role='doctor'
        )
    @pytest.fixture
    def drug(self):
        return Drug.objects.create(
            name='TestDrug', description='Desc', price=5.0,
            quantity=10, reorder_threshold=5,
            supplier=Supplier.objects.create(name='S',email='s@x.com',phone='123')
        )
    @pytest.fixture
    def prescription(self, doctor, patient, drug):
        pres = Prescription.objects.create(doctor=doctor, patient=patient)
        PrescriptionDrug.objects.create(prescription=pres, drug=drug, dosage='10mg', quantity=4)
        return pres

    @pytest.fixture
    def client_for(self):
        def make(user):
            client = APIClient()
            tok = client.post(reverse('token_obtain_pair'),
                              {'email': user.email, 'password': user.password})
            client.credentials(HTTP_AUTHORIZATION=f"Bearer {tok.data['access']}")
            return client
        return make

    def test_pharmacist_can_create_and_dispense(self, client_for, pharmacist, prescription, drug, patient):
        client = client_for(pharmacist)
        url = reverse('order-list')
        resp = client.post(url, {'prescription': prescription.id, 'drug': drug.id, 'quantity': 2})
        assert resp.status_code == 201
        order = Order.objects.get(pk=resp.data['id'])
        assert order.status == Order.STATUS_DISPENSED
        drug.refresh_from_db()
        assert drug.quantity == 8  # 10 - 2

    def test_pharmacist_out_of_stock_triggers_reorder(self, client_for, pharmacist, prescription, drug):
        drug.quantity = 1
        drug.save()
        client = client_for(pharmacist)
        resp = client.post(reverse('order-list'), {'prescription': prescription.id, 'drug': drug.id, 'quantity': 4})
        assert resp.status_code == 201
        order = Order.objects.get(pk=resp.data['id'])
        assert order.status == Order.STATUS_PENDING
        # PurchaseOrder auto-created
        assert drug.purchase_orders.filter(status=PurchaseOrder.STATUS_PENDING).exists()

    def test_patient_can_view_own(self, client_for, pharmacist, patient, prescription, drug):
        # pharmacist creates
        order = Order.objects.create(patient=patient, prescription=prescription, drug=drug, quantity=1)
        order.process()
        client = client_for(patient)
        resp = client.get(reverse('order-list'))
        assert resp.status_code == 200
        assert resp.data[0]['patient'] == patient.id

    def test_patient_cannot_create(self, client_for, patient, prescription, drug):
        client = client_for(patient)
        resp = client.post(reverse('order-list'), {'prescription': prescription.id, 'drug': drug.id, 'quantity': 1})
        assert resp.status_code == 403

    def test_unauthenticated(self):
        assert APIClient().get(reverse('order-list')).status_code == 401


