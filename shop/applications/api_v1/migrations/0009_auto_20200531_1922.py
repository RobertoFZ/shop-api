# Generated by Django 3.0.4 on 2020-05-31 19:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api_v1', '0008_subscription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[(0, 'fallido'), (1, 'pago procesando'), (2, 'enviado'), (3, 'completado'), (4, 'cancelado')], max_length=1),
        ),
        migrations.AlterField(
            model_name='product',
            name='collection',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api_v1.Collection'),
        ),
        migrations.CreateModel(
            name='UserSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('started_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('ended_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('last_paid', models.FloatField(default=0.0)),
                ('subscription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_v1.Subscription')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReviewPurchase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('rating', models.IntegerField(default=5, null=True)),
                ('review', models.CharField(max_length=255, null=True)),
                ('product_variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_v1.ProductVariant')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BusinessSetting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('free_delivery_amount', models.FloatField(default=0.0, null=True)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api_v1.Business')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
