from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from shop.applications.common.serializers import Base64ImageField
from shop.applications.api_v1.models import Business, Collection
from shop.settings import URL_SERVER

class CollectionsSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False, label='id')
    name = serializers.CharField(required=True, label='name')
    description = serializers.CharField(required=True, label='description')
    image = Base64ImageField(required=False)
    business_id = serializers.IntegerField(required=True, label='business_id')

    def validate(self, data):
        return data

    def create(self, validated_data, business):
        collection = Collection.objects.create(**validated_data)
        collection.business = business
        collection.save()

        return collection
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        return instance