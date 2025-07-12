import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from .models import Invoice, Payment
from decimal import Decimal

User = get_user_model()

@pytest.mark.django_db
class TestBillingAPI:
    @pytest.fixture
    def patient(self):
        return User.objects.create_user(
            username='pat', email='pat@example.com',
            password='PatPass1!', role='patient'
        )
    @pytest.fixture
    def admin(self):
        return User.objects.create_superuser(
            username='adm', email='adm@example.com',
            password='AdmPass1!'
        )
    @pytest.fixture
    def client_for(self):
        def _make(user):
            client = APIClient()
            tok = client.post(reverse('token_obtain_pair'),
                              {'email': user.email, 'password': user.password})
            client.credentials(HTTP_AUTHORIZATION=f"Bearer {tok.data['access']}")
            return client
        return _make

    def test_admin_can_create_invoice(self, client_for, admin, patient):
        client = client_for(admin)
        resp = client.post(reverse('invoice-list'), {
            'patient': patient.id,
            'amount': '150.00'
        })
        assert resp.status_code == 201
        assert Invoice.objects.filter(patient=patient).exists()

    def test_patient_cannot_create_invoice(self, client_for, patient):
        client = client_for(patient)
        resp = client.post(reverse('invoice-list'), {
            'patient': patient.id,
            'amount': '100.00'
        })
        assert resp.status_code == 403

    def test_patient_can_view_own_invoice(self, client_for, admin, patient):
        inv = Invoice.objects.create(patient=patient, amount=Decimal('200.00'))
        client = client_for(patient)
        resp = client.get(reverse('invoice-detail', args=[inv.id]))
        assert resp.status_code == 200
        assert resp.data['amount'] == '200.00'

    def test_pay_action_creates_payment(self, client_for, admin, patient, mocker):
        inv = Invoice.objects.create(patient=patient, amount=Decimal('120.00'))
        client = client_for(patient)
        # mock the task
        mocked = mocker.patch('billing.tasks.initiate_mpesa_payment.delay')
        resp = client.post(reverse('invoice-pay', args=[inv.id]))
        assert resp.status_code == 202
        payment = Payment.objects.get(invoice=inv)
        mocked.assert_called_once_with(payment.id)

    def test_payment_read_only(self, client_for, patient):
        inv = Invoice.objects.create(patient=patient, amount=Decimal('50.00'))
        pay = Payment.objects.create(invoice=inv, amount=inv.amount)
        client = client_for(patient)
        resp = client.patch(reverse('payment-detail', args=[pay.id]), {'status': 'success'})
        assert resp.status_code == 405  # Method not allowed for ReadOnlyModelViewSet

    def test_unauthenticated_forbidden(self):
        assert APIClient().get(reverse('invoice-list')).status_code == 401
