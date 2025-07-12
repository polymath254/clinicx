import africastalking
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import NotificationLog

logger = get_task_logger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_email_task(self, user_id, recipient_list, subject, template_name, context):
    # Log creation
    log = NotificationLog.objects.create(
        user_id=user_id,
        notification_type=NotificationLog.TYPE_EMAIL,
        recipient=", ".join(recipient_list),
        subject=subject,
        message=render_to_string(template_name, context),
    )
    try:
        html_message = log.message
        send_mail(
            subject=subject,
            message=html_message,  # plain fallback
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        log.status = NotificationLog.STATUS_SENT
        log.response = {}
        log.save(update_fields=['status', 'response', 'updated_at'])
    except Exception as exc:
        logger.exception("Email send failed")
        log.status = NotificationLog.STATUS_FAILED
        log.error_message = str(exc)
        log.save(update_fields=['status', 'error_message', 'updated_at'])
        raise self.retry(exc=exc)
    return log.id

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_sms_task(self, user_id, phone_number, message):
    log = NotificationLog.objects.create(
        user_id=user_id,
        notification_type=NotificationLog.TYPE_SMS,
        recipient=phone_number,
        message=message,
    )
    try:
        africastalking.initialize(
            username=settings.AFRICASTALKING_USERNAME,
            api_key=settings.AFRICASTALKING_API_KEY,
        )
        sms = africastalking.SMS
        response = sms.send(message, [phone_number])
        log.status = NotificationLog.STATUS_SENT
        log.response = response
        log.save(update_fields=['status', 'response', 'updated_at'])
    except Exception as exc:
        logger.exception("SMS send failed")
        log.status = NotificationLog.STATUS_FAILED
        log.error_message = str(exc)
        log.save(update_fields=['status', 'error_message', 'updated_at'])
        raise self.retry(exc=exc)
    return log.id
