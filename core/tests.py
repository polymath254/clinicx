from django.test import TestCase
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import NotFound
from core.exceptions import custom_exception_handler

class ExceptionHandlerTest(TestCase):
    def test_custom_exception_includes_status(self):
        factory = APIRequestFactory()
        request = factory.get('/')
        exc = NotFound('Not found')
        response = custom_exception_handler(exc, {'request': request})
        self.assertEqual(response.data.get('detail'), 'Not found')
        self.assertEqual(response.data.get('status_code'), 404)
