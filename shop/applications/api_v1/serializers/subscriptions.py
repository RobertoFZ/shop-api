from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from shop.applications.api_v1.models import Subscription, SubscriptionPayment
from shop.settings import URL_SERVER


class SubscriptionsSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False, label='id')
    name = serializers.CharField(required=True, label='name')
    price = serializers.FloatField(required=True, label='price')
    period = serializers.IntegerField(required=True, label='period')
    period_number = serializers.IntegerField(
        required=True, label='period_number')

    def validate(self, data):
        return data

    def create(self, validated_data):
        subscription = Subscription.objects.create(**validated_data)
        subscription.save()

        return subscription

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.price = validated_data.get('price', instance.price)
        instance.period = validated_data.get('period', instance.period)
        instance.period_number = validated_data.get(
            'period_number', instance.period_number)
        instance.save()

        return instance


class SubscriptionPaymentSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False, label='id')
    amount = serializers.FloatField(required=True, label='amount')
    order_id = serializers.CharField(required=True, label='order_id')
    openpay_status_text = serializers.CharField(
        required=True, label='status text')
    error_message = serializers.CharField(required=True, label='error message')
