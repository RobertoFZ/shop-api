from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from shop.applications.common.serializers import Base64ImageField
from shop.applications.api_v1.models import ProductImage
from shop.settings import URL_SERVER


class ProductImageSerializer(serializers.Serializer):
    """
       Serializer for account profile
       """
    id = serializers.IntegerField(required=False, label='id')
    image = Base64ImageField(required=True)

    def validate(self, data):
        # Create validations if is necessary
        return data

    def create(self, validated_data, product):
        product_image = ProductImage.objects.create(**validated_data)
        product_image.product = product
        product_image.save()

        return product_image
