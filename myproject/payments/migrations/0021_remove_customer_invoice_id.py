# Generated by Django 5.1 on 2024-08-29 09:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0020_subscription_invoice_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='invoice_id',
        ),
    ]
