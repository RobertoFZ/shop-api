# Generated by Django 3.0.4 on 2020-05-02 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_v1', '0005_order_business'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='amount',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='order',
            name='authorization',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='order',
            name='error_message',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='openpay_id',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='order',
            name='openpay_status_text',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='orderproduct',
            name='price',
            field=models.FloatField(default=0),
        ),
    ]
