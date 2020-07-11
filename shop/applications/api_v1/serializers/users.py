from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from shop.applications.common.serializers import Base64ImageField
from shop.applications.api_v1.models import User, Profile
from shop.settings import URL_SERVER


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['image_profile', 'facebook_id']

    image_profile = Base64ImageField(required=False)


class UserSerializer(serializers.Serializer):
    """
       Serializer for account profile
       """
    id = serializers.IntegerField(required=False, label='id')
    first_name = serializers.CharField(required=True, label='first_name')
    last_name = serializers.CharField(required=True, label='last_name')
    email = serializers.CharField(required=True, label='email')
    password = serializers.CharField(required=False, label='password')
    token = serializers.SerializerMethodField()
    profile = ProfileSerializer()

    def validate(self, data):
        keys = data.keys()
        try:
            user = User.objects.get(email=data['email'])
            if 'id' in keys:
                if not user.id == data['id']:
                    raise serializers.ValidationError(
                        _('El correo %s ya se encuentra en uso' % data['email']))
                else:
                    return data
            else:
                raise serializers.ValidationError(
                    _('El correo %s ya se encuentra en uso' % data['email']))
        except User.DoesNotExist:
            return data
        return data

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        user = User.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        profile = Profile.objects.create(user=user, **profile_data)
        user.profile = profile
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        # Unless the application properly enforces that this field is
        # always set, the following could raise a `DoesNotExist`, which
        # would need to be handled.
        profile = instance.profile

        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)

        email = validated_data.get('email', instance.email)
        if not email == instance.email:
            instance.email = email
        instance.save()

        profile.facebook_id = profile_data.get(
            'facebook_id', profile.facebook_id)
        profile.image_profile = profile_data.get(
            'email', profile.image_profile)
        profile.save()

        instance.profile = profile

        return instance

    def get_token(self, data):
        if data.id:
            token, created = Token.objects.get_or_create(user__id=data.id)
            return token.key
        else:
            return None
