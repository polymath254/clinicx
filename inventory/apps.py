from django.apps import AppConfig

class InventoryConfig(AppConfig):
    name = 'inventory'
    def ready(self):
        import inventory.signals  # noqa
