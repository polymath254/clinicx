from django.apps import AppConfig

class PrescriptionsConfig(AppConfig):
    name = 'prescriptions'

    def ready(self):
        # No signals yet; placeholder for future hooks
        pass
