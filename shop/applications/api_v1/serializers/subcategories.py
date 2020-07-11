from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from shop.applications.common.serializers import Base64ImageField
from shop.applications.api_v1.models import Business, Category, SubCategory
from shop.applications.api_v1.serializers.categories import CategoriesSerializer
from shop.settings import URL_SERVER


class SubCategoriesSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False, label='id')
    name = serializers.CharField(required=True, label='name')
    description = serializers.CharField(required=True, label='description')
    image = Base64ImageField(required=False)
    category_id = serializers.IntegerField(required=False, label='category_id')
    category = CategoriesSerializer(read_only=True)

    def validate(self, data):
        return data

    def create(self, validated_data, category):
        subcategory = SubCategory.objects.create(**validated_data)
        subcategory.category = category
        subcategory.save()

        return subcategory

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.category_id = validated_data.get('category_id', instance.category_id)
        instance.description = validated_data.get(
            'description', instance.description)
        new_image = validated_data.get(
            'image', None)
        if not new_image == None:
            instance.image.delete()
            instance.image = new_image
        instance.save()

        return instance
