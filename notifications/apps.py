from django.apps import AppConfig

class NotificationsConfig(AppConfig):
    name = 'notifications'

    def ready(self):
        # nothing to import here; tasks are invoked externally
        pass
