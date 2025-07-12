from django.apps import AppConfig

class AppointmentsConfig(AppConfig):
    name = 'appointments'

    def ready(self):
        # If you add signals for notifications, import them here.
        pass
