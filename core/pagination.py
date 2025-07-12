from django.conf import settings
from rest_framework.pagination import PageNumberPagination

class DefaultPagination(PageNumberPagination):
    """
    Default pagination using page size from settings and allowing client override up to a max.
    """
    page_size = settings.REST_FRAMEWORK.get('PAGE_SIZE', 10)
    page_size_query_param = 'page_size'
    max_page_size = 100
