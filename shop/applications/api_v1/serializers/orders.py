from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from shop.applications.api_v1.models import Order, OrderProduct
from shop.applications.api_v1.serializers.business import BusinessSerializer
from shop.applications.api_v1.serializers.customers import CustomerSerializer
from shop.applications.api_v1.serializers.order_products import OrderProductSerializer
from shop.settings import URL_SERVER


class OrderSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False, label='id')
    business_id = serializers.IntegerField(required=False, label='business id')
    customer_id = serializers.IntegerField(required=True, label='customer_id')
    order_id = serializers.CharField(required=True, label='Order business id')
    openpay_id = serializers.CharField(required=True, label='OpenPay ID')
    openpay_order_id = serializers.CharField(
        required=True, label='OpenPay order ID')
    authorization = serializers.CharField(
        required=True, label='Bank authorization')
    openpay_status_text = serializers.CharField(
        required=True, label='OpenPay status text')
    error_message = serializers.CharField(
        required=False, label='OpenPay error message')
    shipping_track_id = serializers.CharField(
        required=False, label='Shipping tracking id')
    status = serializers.IntegerField(
        required=True, label='The current status')
    amount = serializers.FloatField(required=True, label='Total amount')
    shipping_cost = serializers.FloatField(
        required=True, label='Shipping cost')
    customer = CustomerSerializer(read_only=True)
    business = BusinessSerializer(read_only=True)
    order_products = serializers.SerializerMethodField()
    method = serializers.CharField(required=True, label='Payment Method Service')

    def get_order_products(self, order):
        order_products = OrderProduct.objects.filter(order=order)
        return OrderProductSerializer(order_products, many=True).data

    def validate(self, data):
        return data

    def create(self, validated_data, business):
        order = Order.objects.create(**validated_data)
        order.business = business
        order.save()

        return order

    def update(self, order, validated_data):
        order.shipping_track_id = validated_data.get(
            'shipping_track_id', order.shipping_track_id)
        order.status = validated_data.get('status', order.status)
        order.save()

        return order
