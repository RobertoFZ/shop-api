from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from datetime import datetime

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated

from shop.applications.api_v1.models import User, Subscription, UserSubscription
from shop.settings import URL_SERVER
from shop.applications.api_v1.serializers.user_subscriptions import UserSubscriptionSerializer, UserSubscriptionDataSerializer

@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class UserSubscriptionCreate(APIView):
    serializer_class = UserSubscriptionSerializer
    serializer_class_data = UserSubscriptionDataSerializer

    def post(self, request, user_pk):
        try:
            user = User.objects.get(id=user_pk)
        except User.DoesNotExist:
            return Response({'message', _('No se encontró el usuario.')}, status=status.HTTP_400_BAD_REQUEST)  

        try:
            subscription = Subscription.objects.get(id=request.data['subscription_id'])  
        except Subscription.DoesNotExist:             
            return Response({'message', _('No se encontró la suscripción.')}, status=status.HTTP_400_BAD_REQUEST)  
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                timestamp_started_date = serializer.validated_data['started_date']
                serializer.validated_data['started_date'] = datetime.fromtimestamp(timestamp_started_date)

                timestamp_ended_date = serializer.validated_data['ended_date']
                serializer.validated_data['ended_date'] = datetime.fromtimestamp(timestamp_ended_date)                                                                            
            except:
                pass
            user_subscription = serializer.create(serializer.validated_data, user, subscription)
            response = self.serializer_class_data(user_subscription).data
            return Response(response, status=status.HTTP_201_CREATED)


        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class UserSubscriptionView(APIView):
    serializer_class = UserSubscriptionSerializer
    serializer_class_data = UserSubscriptionDataSerializer

    def get(self, request, user_pk, user_subscription_pk):
        try:
            user = User.objects.get(id=user_pk)
        except User.DoesNotExist:
            return Response({'message', _('No se encontró el usuario.')}, status=status.HTTP_400_BAD_REQUEST)  
        
        try:
            user_subscription = UserSubscription.objects.get(id=user_subscription_pk)
        except UserSubscription.DoesNotExist:
            return Response({'message', _('No cuentas con suscripción.')}, status=status.HTTP_400_BAD_REQUEST)  
        
        serializer = self.serializer_class_data(user_subscription)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, user_pk, user_subscription_pk):
        try:
            user = User.objects.get(id=user_pk)
        except User.DoesNotExist:
            return Response({'message', _('No se encontró el usuario.')}, status=status.HTTP_400_BAD_REQUEST)  
        
        try:
            user_subscription = UserSubscription.objects.get(id=user_subscription_pk)
        except UserSubscription.DoesNotExist:
            return Response({'message', _('No cuentas con suscripción.')}, status=status.HTTP_400_BAD_REQUEST)

        user_subscription.deleted_at = timezone.now()
        user_subscription.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
