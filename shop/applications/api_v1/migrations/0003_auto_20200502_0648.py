# Generated by Django 3.0.4 on 2020-05-02 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_v1', '0002_auto_20200502_0645'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='shipping_track_id',
        ),
        migrations.AddField(
            model_name='productvariant',
            name='shipping_price',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
    ]
