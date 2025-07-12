from django.apps import AppConfig

class CoreConfig(AppConfig):
    name = 'core'
    verbose_name = 'Core'

    def ready(self):
        # Place for startup checks or imports (e.g. signals)
        pass
