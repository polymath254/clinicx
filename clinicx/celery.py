import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinicx.settings')

app = Celery('clinicx')

# Using a string here means the worker does not have to pickle
# the object when using Windows.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Optional: custom beat schedule for periodic tasks
app.conf.beat_schedule = {
    # daily inventory reorder check at 2am
    'daily-inventory-check': {
        'task': 'inventory.tasks.check_reorders',
        'schedule':  crontab(hour=2, minute=0),
    },
    # weekly summary email Monday 6am
    'weekly-sales-report': {
        'task': 'notifications.tasks.send_email_task',
        'schedule': crontab(day_of_week='mon', hour=6, minute=0),
        'args': (
            None,
            ['admin@clinicx.com'],
            'Weekly Sales Report',
            'emails/weekly_report.html',
            {'report_data': 'TODO'},
        ),
    },
}

