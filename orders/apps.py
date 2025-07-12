from django.apps import AppConfig

class OrdersConfig(AppConfig):
    name = 'orders'
    def ready(self):
        # no signals needed here; logic in model.process()
        pass
