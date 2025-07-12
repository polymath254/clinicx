import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from inventory.models import Supplier, Drug, PurchaseOrder

User = get_user_model()

@pytest.mark.django_db
class TestInventoryAPI:
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
    def client_for(self):
        def _make(user):
            client = APIClient()
            resp = client.post(reverse('token_obtain_pair'),
                               {'email': user.email, 'password': user.password})
            client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
            return client
        return _make

    @pytest.fixture
    def supplier(self):
        return Supplier.objects.create(name='Sup', email='sup@example.com', phone='123456')

    def test_supplier_crud(self, client_for, pharmacist, admin, supplier):
        client_ph = client_for(pharmacist)
        # LIST
        assert client_ph.get(reverse('supplier-list')).status_code == 200
        # CREATE
        resp = client_ph.post(reverse('supplier-list'), {'name':'New','email':'n@example.com','phone':'000'})
        assert resp.status_code == 201
        # ADMIN update
        client_ad = client_for(admin)
        resp2 = client_ad.patch(reverse('supplier-detail', args=[supplier.id]), {'phone':'999'})
        assert resp2.status_code == 200
        # PATIENT forbidden
        patient = User.objects.create_user('pat','pat@example.com','Pat1!','patient')
        client_pa = client_for(patient)
        assert client_pa.get(reverse('supplier-list')).status_code == 403

    @pytest.fixture
    def drug(self, supplier):
        return Drug.objects.create(
            name='Drug1', description='Desc', price=10.5,
            quantity=50, reorder_threshold=20, supplier=supplier
        )

    def test_drug_properties_and_crud(self, client_for, pharmacist, drug):
        assert not drug.needs_reorder
        drug.quantity = 10
        assert drug.needs_reorder
        # CRUD
        client_ph = client_for(pharmacist)
        assert client_ph.get(reverse('drug-list')).status_code == 200
        resp = client_ph.post(reverse('drug-list'), {
            'name':'Drug2','description':'d','price':5,'quantity':30,
            'reorder_threshold':10,'supplier':drug.supplier.id
        })
        assert resp.status_code == 201

    @pytest.fixture
    def purchase_order(self, supplier, drug):
        return PurchaseOrder.objects.create(supplier=supplier, drug=drug, quantity=20)

    def test_purchase_order_deliver_action(self, client_for, pharmacist, purchase_order):
        client_ph = client_for(pharmacist)
        resp = client_ph.post(reverse('purchaseorder-deliver', args=[purchase_order.id]))
        assert resp.status_code == 200
        assert resp.data['status'] == PurchaseOrder.STATUS_DELIVERED

    def test_create_po_negative_quantity(self, client_for, pharmacist, supplier, drug):
        resp = client_for(pharmacist).post(reverse('purchaseorder-list'),
                                           {'supplier':supplier.id,'drug':drug.id,'quantity':-5})
        assert resp.status_code == 400

    def test_unauthenticated_forbidden(self):
        assert APIClient().get(reverse('supplier-list')).status_code == 401
    