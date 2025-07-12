from django.apps import AppConfig

class PatientsConfig(AppConfig):
    name = 'patients'

    def ready(self):
        import patients.signals  # noqa
