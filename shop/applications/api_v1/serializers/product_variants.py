from django.utils.translation import ugettext_lazy as _

from datetime import datetime
from rest_framework import serializers
from shop.settings import URL_SERVER
from shop.applications.api_v1.models import ProductVariant
from shop.applications.api_v1.serializers.product_images import ProductImageSerializer


class ProductVariantSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False, label="id")
    name = serializers.CharField(required=True, label="name")
    price = serializers.FloatField(
        required=False, label="new price")
    shipping_price = serializers.FloatField(
        required=False, label="new shipping price")
    sku = serializers.CharField(required=True, label="sku")
    stock = serializers.IntegerField(required=False, label="current stock")
    use_stock = serializers.BooleanField(
        required=False, label="shuld use stock?")
    product_id = serializers.IntegerField(required=False, label="product_id")
    product_name = serializers.SerializerMethodField()

    def get_product_name(self, data):
        try:
            return data.product.name
        except:
            return ''

    def validate(self, data):
        return data

    def create(self, validated_data, business):
        product_variant = ProductVariant.objects.create(**validated_data)
        product_variant.save()
        return product_variant

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.price = validated_data.get('price', instance.price)
        instance.shipping_price = validated_data.get(
            'shipping_price', instance.shipping_price)
        instance.sku = validated_data.get(
            'sku', instance.sku)
        instance.stock = validated_data.get(
            'stock', instance.stock)
        instance.use_stock = validated_data.get(
            'use_stock', instance.use_stock)
        instance.save()

        return instance
