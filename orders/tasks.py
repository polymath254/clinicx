from celery import shared_task
from django.conf import settings
import africastalking

africastalking.initialize(
    username=settings.AFRICASTALKING_USERNAME,
    api_key=settings.AFRICASTALKING_API_KEY
)
sms = africastalking.SMS

@shared_task
def send_order_sms_task(phone_number, message):
    print(f"Celery task called with: {phone_number} - {message}")
    if not phone_number:
        print("No phone number provided, SMS not sent.")
        return
    try:
        # You can omit the "from" parameter for sandbox
        response = sms.send(message, [phone_number])
        print(f"Africa's Talking response: {response}")
    except Exception as e:
        print(f"Error sending SMS: {e}")

