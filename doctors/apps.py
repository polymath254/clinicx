from django.apps import AppConfig

class DoctorsConfig(AppConfig):
    name = 'doctors'

    def ready(self):
        import doctors.signals  # noqa
