import requests, base64, datetime
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from .models import Payment, Invoice

logger = get_task_logger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def initiate_mpesa_payment(self, payment_id):
    payment = Payment.objects.select_related('invoice__patient').get(pk=payment_id)
    invoice = payment.invoice
    user_phone = str(invoice.patient.phone_number)
    # 1. Get OAuth token
    try:
        auth = requests.get(
            f"{settings.MPESA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials",
            auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET)
        )
        auth.raise_for_status()
        access_token = auth.json()['access_token']
    except Exception as exc:
        logger.exception("Failed to get access token")
        raise self.retry(exc=exc)

    # 2. Build STK push password
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    raw_pass = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
    stk_password = base64.b64encode(raw_pass.encode()).decode()

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": stk_password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": str(invoice.amount),
        "PartyA": user_phone,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": user_phone,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": f"INV{invoice.id}",
        "TransactionDesc": f"Payment for invoice {invoice.id}"
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(f"{settings.MPESA_BASE_URL}/mpesa/stkpush/v1/processrequest",
                             json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # Save checkout request ID
        payment.mpesa_checkout_request_id = data.get("CheckoutRequestID")
        payment.save(update_fields=["mpesa_checkout_request_id"])
        return data
    except Exception as exc:
        logger.exception("STK Push failed")
        payment.status = Payment.STATUS_FAILED
        payment.save(update_fields=["status"])
        raise self.retry(exc=exc)
