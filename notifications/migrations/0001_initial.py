# Generated by Django 5.2.4 on 2025-07-12 11:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('email', 'Email'), ('sms', 'SMS')], max_length=10)),
                ('recipient', models.CharField(help_text='Email address or phone number.', max_length=255)),
                ('subject', models.CharField(blank=True, max_length=255, null=True)),
                ('message', models.TextField()),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('sent', 'Sent'), ('failed', 'Failed')], default='pending', max_length=10)),
                ('response', models.JSONField(blank=True, help_text='Provider response payload, if any.', null=True)),
                ('error_message', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, help_text='User who triggered this notification, if any.', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Notification Log',
                'verbose_name_plural': 'Notification Logs',
                'indexes': [models.Index(fields=['notification_type'], name='notificatio_notific_be328b_idx'), models.Index(fields=['status'], name='notificatio_status_a242db_idx'), models.Index(fields=['recipient'], name='notificatio_recipie_8b135e_idx')],
            },
        ),
    ]
