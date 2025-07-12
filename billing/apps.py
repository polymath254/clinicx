from django.apps import AppConfig

class BillingConfig(AppConfig):
    name = 'billing'

    def ready(self):
        # No signals yet; callback handled externally
        pass
