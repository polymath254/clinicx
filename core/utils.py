from django.utils import timezone

def now_utc():
    """
    Return current time with UTC timezone.
    """
    return timezone.now()
