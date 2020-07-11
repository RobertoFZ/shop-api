from django.utils.translation import ugettext_lazy as _

from datetime import datetime
from rest_framework import serializers
from shop.settings import URL_SERVER
from shop.applications.api_v1.models import Product, ProductImage, ProductVariant, ReviewPurchase
from shop.applications.api_v1.serializers.business import BusinessSerializer
from shop.applications.api_v1.serializers.product_images import ProductImageSerializer
from shop.applications.api_v1.serializers.product_variants import ProductVariantSerializer
from shop.applications.api_v1.serializers.subcategories import SubCategoriesSerializer
from shop.applications.api_v1.serializers.review_purchases import ReviewPurchaseSerializer


class ProductSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False, label="id")
    name = serializers.CharField(required=True, label="name")
    description = serializers.CharField(required=True, label="description")
    price = serializers.FloatField(required=True, label="price")
    shipping_price = serializers.FloatField(
        required=True, label="shipping price")
    published = serializers.BooleanField(required=False, label="published")
    publish_at = serializers.FloatField(required=False, label="published_at")
    promote = serializers.BooleanField(required=False, label="promote")
    engine_title = serializers.CharField(required=False, label="engine_title")
    engine_description = serializers.CharField(
        required=False, label="engine_description")
    business_id = serializers.IntegerField(required=False, label="business_id")
    subcategory_id = serializers.IntegerField(
        required=False, label="subcategory_id")
    collection_id = serializers.IntegerField(
        required=False, label="collection_id")

    def validate(self, data):
        return data

    def create(self, validated_data, business):
        product = Product.objects.create(**validated_data)
        product.business = business
        product.save()

        return product

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.shipping_price = validated_data.get(
            'shipping_price', instance.shipping_price)
        instance.published = validated_data.get(
            'published', instance.published)
        instance.publish_at = validated_data.get(
            'publish_at', instance.publish_at)
        instance.subcategory_id = validated_data.get(
            'subcategory_id', instance.subcategory_id)
        instance.collection_id = validated_data.get(
            'collection_id', instance.collection_id)
        instance.promote = validated_data.get('promote', instance.promote)
        instance.engine_title = validated_data.get(
            'engine_title', instance.engine_title)
        instance.engine_description = validated_data.get(
            'engine_description', instance.engine_description)
        instance.save()

        return instance


class ProductDataSerializer(serializers.ModelSerializer):
    publish_at = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    product_variants = serializers.SerializerMethodField()
    review_purchase = serializers.SerializerMethodField()
    subcategory = SubCategoriesSerializer(read_only=True)
    business = BusinessSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "description", "price", "shipping_price", "published", "publish_at", "promote",
                  "engine_title", "engine_description", "business_id", "subcategory_id", "collection_id", "images", "product_variants", "review_purchase","subcategory", "business"]

    def get_publish_at(self, obj):
        return datetime.timestamp(obj.publish_at)

    def get_images(self, obj):
        images = ProductImage.objects.filter(product=obj).order_by('created_at')
        return ProductImageSerializer(images, many=True).data

    def get_product_variants(self, obj):
        product_variants = ProductVariant.objects.filter(
            product=obj, deleted_at=None).order_by('created_at')
        return ProductVariantSerializer(product_variants, many=True).data
    
    def get_review_purchase(self, obj):        
        reviewTotal = 0     
        i = 0           
        try:
            review_purchase = ReviewPurchase.objects.filter(product_variant__product_id=obj)
            
            for total in review_purchase:               
                reviewTotal += total.rating        
                i += 1    
            if reviewTotal == 0 and i == 0:
                return None
            else:
                return(reviewTotal/i)        
        except ReviewPurchase.DoesNotExist:
            return None
