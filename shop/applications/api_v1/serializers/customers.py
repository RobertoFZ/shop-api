from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from shop.applications.api_v1.models import Customer
from shop.settings import URL_SERVER


class CustomerSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False, label='id')
    business_id = serializers.IntegerField(required=False, label='business id')
    name = serializers.CharField(max_length=255, label='name')
    email = serializers.CharField(max_length=255, label='email')
    address = serializers.CharField(max_length=255, label='address')
    colony = serializers.CharField(max_length=255, label='colony')
    city = serializers.CharField(max_length=255, label='city')
    state = serializers.CharField(max_length=255, label='state')
    zip = serializers.CharField(max_length=255, label='zip')
    country = serializers.CharField(max_length=255, label='country')
    phone = serializers.CharField(max_length=255, label='phone')

    def validate(self, data):
        return data

    def create(self, validated_data, business):
        customer = Customer.objects.create(**validated_data)
        customer.business = business
        customer.save()

        return customer

    def update(self, customer, validated_data):
        customer.name = validated_data.get(
            'name', customer.name)
        customer.email = validated_data.get(
            'email', customer.email)
        customer.address = validated_data.get('address', customer.address)
        customer.colony = validated_data.get('colony', customer.colony)
        customer.city = validated_data.get('city', customer.city)
        customer.state = validated_data.get('state', customer.state)
        customer.zip = validated_data.get('zip', customer.zip)
        customer.country = validated_data.get('country', customer.country)
        customer.phone = validated_data.get('phone', customer.phone)
        customer.save()

        return customer
