# Generated by Django 5.1 on 2024-08-28 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0017_remove_subscription_invoice_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='stri_subscription_id',
            field=models.CharField(default=1, editable=False, max_length=100),
            preserve_default=False,
        ),
    ]
