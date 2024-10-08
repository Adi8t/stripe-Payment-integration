# Generated by Django 5.0.6 on 2024-06-28 08:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stri_customer_id', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.AddField(
            model_name='price',
            name='stri_price_id',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='stri_product_id',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stri_subscription_id', models.CharField(max_length=100, null=True)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payments.customer')),
                ('price', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payments.price')),
            ],
        ),
    ]
