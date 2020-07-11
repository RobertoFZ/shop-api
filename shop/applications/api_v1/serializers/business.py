from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from shop.applications.common.serializers import Base64ImageField
from shop.applications.api_v1.models import User, Profile, Business, BusinessSetting
from shop.applications.api_v1.serializers.users import UserSerializer
from shop.applications.api_v1.serializers.business_settings import BussinesSettingSerializer
from shop.settings import URL_SERVER


class BusinessSerializer(serializers.Serializer):
    """
       Serializer for account profile
       """
    id = serializers.IntegerField(required=False, label='id')
    name = serializers.CharField(required=True, label='name')
    description = serializers.CharField(required=True, label='description')
    active = serializers.BooleanField(required=False, label='active')
    logo = Base64ImageField(required=False)
    users = serializers.SerializerMethodField()
    # business_settings = BussinesSettingSerializer(read_only=True)
    business_settings = serializers.SerializerMethodField()

    def validate(self, data):
        # Create validations if is necessary
        return data

    def create(self, validated_data, user):
        business = Business.objects.create(**validated_data)
        business.save()

        business.users.add(user)
        business.save()

        return business

    def update(self, instance, validated_data):
        instance.name = validated_data.get(
            'name', instance.name)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.active = validated_data.get(
            'active', instance.active)

        new_logo = validated_data.get(
            'logo', None)
        if not new_logo == None:
            instance.logo.delete()
            instance.logo = new_logo
        instance.save()

        return instance

    def get_users(self, business):
        if business.id:
            return business.users.all().values_list('id', flat=True)
        else:
            return []
    
    def get_business_settings(self, obj):
        try:
            business_settings = BusinessSetting.objects.get(business=obj)
            return BussinesSettingSerializer(business_settings).data
        except BusinessSetting.DoesNotExist:
            return None