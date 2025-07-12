import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from notifications.models import NotificationLog
from notifications.tasks import send_email_task, send_sms_task

User = get_user_model()

@pytest.mark.django_db
class TestNotifications:

    @pytest.fixture
    def admin(self):
        return User.objects.create_superuser('adm', 'adm@example.com', 'AdmPass1!')

    @pytest.fixture
    def patient(self):
        return User.objects.create_user('pat','pat@example.com','PatPass1!','patient')

    @pytest.fixture
    def client_for(self):
        def make(user):
            client = APIClient()
            resp = client.post(reverse('token_obtain_pair'),
                               {'email': user.email, 'password': user.password})
            client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")
            return client
        return make

    def test_send_email_task_creates_log_and_sends(self, patient, settings):
        # override send_mail to avoid real emails
        settings.DEFAULT_FROM_EMAIL = 'no-reply@test.com'
        user_id = patient.id
        # run task synchronously
        log_id = send_email_task.run(user_id, ['test@x.com'], 'Subj',
                                     'notifications/email_test.html', {'foo':'bar'})
        log = NotificationLog.objects.get(pk=log_id)
        assert log.notification_type == NotificationLog.TYPE_EMAIL
        assert log.status in [NotificationLog.STATUS_SENT, NotificationLog.STATUS_FAILED]

    def test_send_sms_task_creates_log(self, patient):
        from notifications.tasks import send_sms_task
        log_id = send_sms_task.run(patient.id, '+1234567890', 'Hello')
        log = NotificationLog.objects.get(pk=log_id)
        assert log.notification_type == NotificationLog.TYPE_SMS
        assert log.recipient == '+1234567890'

    def test_admin_can_view_logs(self, client_for, admin):
        # create a dummy log
        NotificationLog.objects.create(
            notification_type=NotificationLog.TYPE_SMS,
            recipient='+1', message='m', status=NotificationLog.STATUS_SENT
        )
        client = client_for(admin)
        resp = client.get(reverse('notification-log-list'))
        assert resp.status_code == 200
        assert len(resp.data) >= 1

    def test_non_admin_forbidden(self, client_for, patient):
        client = client_for(patient)
        assert client.get(reverse('notification-log-list')).status_code == 403

    def test_unauthenticated_forbidden(self):
        client = APIClient()
        assert client.get(reverse('notification-log-list')).status_code == 401
