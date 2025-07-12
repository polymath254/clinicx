from django.apps import AppConfig

class UsersConfig(AppConfig):
    name = 'users'
    verbose_name = 'Users'

    def ready(self):
        # Import signals or perform startup tasks here
        try:
            import users.signals  # noqa
        except ImportError:
            pass
