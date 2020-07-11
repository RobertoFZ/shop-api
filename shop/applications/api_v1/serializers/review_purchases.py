from django.utils.translation import ugettext_lazy as _

from datetime import datetime
from rest_framework import serializers
from shop.settings import URL_SERVER
from shop.applications.api_v1.models import ReviewPurchase

class ReviewPurchaseSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False, label='id')
    rating = serializers.IntegerField(required=False, label='rating')
    review = serializers.CharField(required=False, label='review')
    product_variant_id = serializers.IntegerField(required=False, label='product_variant_id')

    def validate(self, data):
        return data
    
    def create(self, validated_data, product_variant):
        review_purchase = ReviewPurchase.objects.create(**validated_data)
        review_purchase.product_variant = product_variant
        review_purchase.save()

        return review_purchase