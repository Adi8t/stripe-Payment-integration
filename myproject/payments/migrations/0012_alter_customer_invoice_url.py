# Generated by Django 5.1 on 2024-08-22 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0011_customer_invoice_id_customer_invoice_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='invoice_url',
            field=models.CharField(editable=False, max_length=200, null=True),
        ),
    ]
