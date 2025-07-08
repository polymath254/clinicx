from django.test import TestCase
from rest_framework.test import APIClient
from customers.models import Customer
from orders.models import Order
from django.contrib.auth import get_user_model

class TestOrderAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='orderuser', password='orderpass123'
        )
        resp = self.client.post('/api/token/', {
            'username': 'orderuser', 'password': 'orderpass123'
        })
        self.token = resp.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.customer = Customer.objects.create(name='Bob', code='C002', phone_number='+254700000002')
        self.order = Order.objects.create(customer=self.customer, item='Panadol', amount=100)

    def test_create_order(self):
        data = {
            'customer': self.customer.id,
            'item': 'Aspirin',
            'amount': 150,
        }
        response = self.client.post('/api/orders/', data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.count(), 2)
        self.assertEqual(Order.objects.get(item='Aspirin').amount, 150)

    def test_create_order_missing_field(self):
        data = {
            'customer': self.customer.id,
            # 'item' missing
            'amount': 200,
        }
        response = self.client.post('/api/orders/', data)
        self.assertEqual(response.status_code, 400)

    def test_create_order_invalid_customer(self):
        data = {
            'customer': 999,  # customer doesn't exist
            'item': 'Paracetamol',
            'amount': 100,
        }
        response = self.client.post('/api/orders/', data)
        self.assertEqual(response.status_code, 400)

    def test_list_orders(self):
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)  # Only self.order by default

    def test_unauthenticated_access(self):
        self.client.credentials()  # remove authentication
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, 401)

    def test_update_order(self):
        response = self.client.patch(f'/api/orders/{self.order.id}/', {'item': 'Paracetamol'})
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.item, 'Paracetamol')

    def test_delete_order(self):
        response = self.client.delete(f'/api/orders/{self.order.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())

    def test_get_single_order(self):
        response = self.client.get(f'/api/orders/{self.order.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['item'], 'Panadol')

    def test_get_nonexistent_order(self):
        response = self.client.get('/api/orders/9999/')
        self.assertEqual(response.status_code, 404)

    def test_create_order_with_blank_item(self):
        data = {'customer': self.customer.id, 'item': '', 'amount': 100}
        response = self.client.post('/api/orders/', data)
        self.assertEqual(response.status_code, 400)

    def test_create_order_with_negative_amount(self):
        data = {'customer': self.customer.id, 'item': 'TestDrug', 'amount': -5}
        response = self.client.post('/api/orders/', data)
        self.assertEqual(response.status_code, 400)

    def test_cascade_delete(self):
        # Delete the customer, should delete their orders
        self.client.delete(f'/api/customers/{self.customer.id}/')
        self.assertFalse(Order.objects.filter(customer=self.customer).exists())

