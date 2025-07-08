from django.test import TestCase
from rest_framework.test import APIClient
from customers.models import Customer
from django.contrib.auth import get_user_model

class TestCustomerAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='testuser', password='testpass123'
        )
        response = self.client.post('/api/token/', {
            'username': 'testuser', 'password': 'testpass123'
        })
        self.token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.customer = Customer.objects.create(name='Jane', code='C001', phone_number='+254700000000')

    def test_create_customer(self):
        data = {'name': 'Polymath Chacha', 'code': 'PC002', 'phone_number': '+254763000000'}
        response = self.client.post('/api/customers/', data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Customer.objects.count(), 2)
        self.assertEqual(Customer.objects.get(code='PC002').name, 'Polymath Chacha')

    def test_list_customers(self):
        response = self.client.get('/api/customers/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)  # 1 customer setUp

    def test_create_duplicate_customer_code(self):
        data = {'name': 'John', 'code': 'C001', 'phone_number': '+254700000001'}
        response = self.client.post('/api/customers/', data)
        self.assertEqual(response.status_code, 400)

    def test_update_customer(self):
        response = self.client.patch(f'/api/customers/{self.customer.id}/', {'name': 'Janet'})
        self.assertEqual(response.status_code, 200)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.name, 'Janet')

    def test_delete_customer(self):
        response = self.client.delete(f'/api/customers/{self.customer.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Customer.objects.filter(id=self.customer.id).exists())

    def test_get_single_customer(self):
        response = self.client.get(f'/api/customers/{self.customer.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], 'Jane')

    def test_get_nonexistent_customer(self):
        response = self.client.get('/api/customers/9999/')
        self.assertEqual(response.status_code, 404)

