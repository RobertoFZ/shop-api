from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from shop.applications.api_v1.models import BusinessSetting
from shop.settings import URL_SERVER

class BussinesSettingSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False, label="id")
    free_delivery_amount = serializers.FloatField(required=False, label="free_delivery_amount")
    business_id = serializers.IntegerField(required=False, label="business_id")

    def validate(self, data):
        return data
    
    def create(self, validated_data, business):
        business_settings = BusinessSetting.objects.create(**validated_data)
        business_settings.business = business
        business_settings.save()

        return business_settings

    def update(self, instance, validated_data):
        instance.free_delivery_amount = validated_data.get(
            'free_delivery_amount', instance.free_delivery_amount)
        instance.save()

        return instance

    

