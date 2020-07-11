from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from shop.applications.api_v1.models import OrderProduct, ProductImage
from shop.settings import URL_SERVER
from shop.applications.api_v1.serializers.product_variants import ProductVariantSerializer
from shop.applications.api_v1.serializers.product_images import ProductImageSerializer


class OrderProductSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False, label='id')
    order_id = serializers.IntegerField(required=False, label='order id')
    product_variant_id = serializers.IntegerField(
        required=False, label='product variant id')
    quantity = serializers.IntegerField(required=True)
    product_variant = ProductVariantSerializer(read_only=True)
    images = serializers.SerializerMethodField()

    def get_images(self, data):
        try:
            images = ProductImage.objects.filter(product=data.product_variant.product_id)
            return ProductImageSerializer(images, many=True).data
        except:
            return []

    def validate(self, data):
        return data

    def create(self, validated_data, order, product_variant):
        order_product = OrderProduct.objects.create(**validated_data)
        order_product.order = order
        order_product.product_variant = product_variant
        order_product.save()

        return order_product

    def update(self, order_product, validated_data):
        order_product.quantity = validated_data.get(
            'quantity', order_product.quantity)
        order_product.save()

        return order_product
