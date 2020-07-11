from django.utils.translation import ugettext_lazy as _

from datetime import datetime
from rest_framework import serializers
from shop.settings import URL_SERVER
from shop.applications.api_v1.models import UserSubscription, User
from shop.applications.api_v1.serializers.users import UserSerializer
from shop.applications.api_v1.serializers.subscriptions import SubscriptionsSerializer

class UserSubscriptionSerializer(serializers.Serializer):

    id = serializers.IntegerField(required=False, label="id")
    started_date = serializers.FloatField(required=True, label="started_date")
    ended_date = serializers.FloatField(required=True, label="ended_date")
    last_paid = serializers.FloatField(required=True, label="last_paid")
    user_id = serializers.IntegerField(required=False, label="user_id")
    subscription_id = serializers.IntegerField(required=False, label="subscription_id")

    def validate(self, data):
        return data
    
    def create(self, validated_data, user, subscription):
        user_subscription = UserSubscription.objects.create(**validated_data)
        user_subscription.user = user
        user_subscription.subscription = subscription
        user_subscription.save()

        return user_subscription
    
    def update(self, instance, validated_data):
        instance.started_date = validated_data.get(
            'started_date', instance.started_date)
        instance.ended_date = validated_data.get(
            'ended_date', instance.ended_date)
        instance.last_pay = validated_data.get(
            'last_pay', instance.last_pay)
        instance.save()

        return instance

class UserSubscriptionDataSerializer(serializers.ModelSerializer):
    started_date = serializers.SerializerMethodField()
    ended_date = serializers.SerializerMethodField()    
    subscription = SubscriptionsSerializer(read_only=True)    

    class Meta:
        model = UserSubscription
        fields = ["id", "started_date", "ended_date", "last_paid", "user_id", "subscription_id", "subscription"]
        
    def get_started_date(self, obj):
        return datetime.timestamp(obj.started_date)
    
    def get_ended_date(self, obj):
        return datetime.timestamp(obj.ended_date)
