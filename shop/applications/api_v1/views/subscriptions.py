from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated

from shop.applications.api_v1.models import Subscription, Order, SubscriptionPayment
from shop.settings import BUSINESS_NAME, URL_SERVER, OPEN_PAY_SUBSCRIPTION_REDIRECT_URL
from shop.applications.api_v1.serializers.subscriptions import SubscriptionsSerializer, SubscriptionPaymentSerializer
from shop.applications.common.openpay import OpenPayManager
from shop.applications.common.functions import generateOrderString


class SubscriptionListView(APIView):
    serializer_class = SubscriptionsSerializer

    def get(self, request):
        try:
            subscription = Subscription.objects.filter(deleted_at=None)
        except Subscription.DoesNotExist:
            return Response({'message', _('No se encontraron las suscripciones.')}, status=status.HTTP_400_BAD_REQUEST)

        response = self.serializer_class(subscription, many=True).data
        return Response(response)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            subscriptions = serializer.create(serializer.validated_data)
            response = self.serializer_class(subscriptions).data
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class SubscriptionView(APIView):
    serializer_class = SubscriptionsSerializer

    def get(self, request, subscription_pk):
        try:
            subscription = Subscription.objects.get(id=subscription_pk)
        except Subscription.DoesNotExist:
            return Response({'message': _('No se encontró la suscripción.')}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(subscription)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, subscription_pk):
        try:
            subscription = Subscription.objects.get(id=subscription_pk)
        except Subscription.DoesNotExist:
            return Response({'message': _('No se encontró la suscripción.')}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            subscription = serializer.update(
                subscription, serializer.validated_data)
            serializer = self.serializer_class(subscription)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, subscription_pk):
        try:
            subscription = Subscription.objects.get(id=subscription_pk)
        except Subscription.DoesNotExist:
            return Response({'message': _('No se encontró la suscripción.')}, status=status.HTTP_404_NOT_FOUND)

        subscription.deleted_at = timezone.now()
        subscription.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class SubscriptionView(APIView):

    def post(self, request):
        try:
            subscription = Subscription.objects.get(
                id=request.data['subscription_id'])
        except Subscription.DoesNotExist:
            return Response({'message': _('No se encontró la suscripción.')}, status=status.HTTP_404_NOT_FOUND)

        keys = request.data.keys()
        # We validates the request body structure
        if not 'subscription_id' in keys and not 'token_id' in keys and not 'device_id' in keys and subscription.price > 0:
            return Response({'message': _('No se puede procesar la orden de compra.')}, status=status.HTTP_400_BAD_REQUEST)

        # Get the user in session
        user = request.user

        # We generate the unique order id
        order_id = self.generate_order_recursively()

        # OpenPay charge response data
        charge_data = None
        if subscription.price > 0:
            token_id = request.data['token_id']
            device_id = request.data['device_id']

            # We obtain the customer, device_id and token_id (OpenPay tokenization)
            open_pay_customer = {
                'name': user.first_name,
                'last_name':  user.last_name,
                'email': user.email
            }
            charge = {
                'customer': open_pay_customer,
                'method': 'card',
                'source_id': token_id,  # The OpenPay token resulting from frontend tokenization
                # We set the amount here and in the Order model
                'amount': round(subscription.price, 2),
                'currency': 'MXN',
                'description': "Pago de suscripción Arca de Troya %s" % (subscription.name),
                'order_id': order_id,
                'device_session_id': device_id,
                'use_3d_secure': True,
                'redirect_url': OPEN_PAY_SUBSCRIPTION_REDIRECT_URL
            }

            # Initialize OpenPayManager
            openpay_manager = OpenPayManager()
            charge_response = openpay_manager.create_charge(charge)
            charge_data = charge_response['data']
            print(charge_data)

            if charge_response['error']:
                return Response({
                    'message': _('Ocurrió un problema al procesar tu pago, no se logró realizar el cargo.'),
                    'error': charge_response['data']
                }, status=status.HTTP_400_BAD_REQUEST)

        suscription_payment = SubscriptionPayment()
        suscription_payment.user = user
        suscription_payment.subscription_name = subscription.name
        suscription_payment.amount = subscription.price
        suscription_payment.order_id = order_id

        # OpenPay ID
        suscription_payment.openpay_id = charge_data['id'] if charge_response else None
        suscription_payment.openpay_order_id = charge_data['order_id'] if charge_response else None
        # OpenPay bank authorization
        suscription_payment.authorization = charge_data['authorization'] if charge_response else None
        # OpenPay status text
        suscription_payment.openpay_status_text = charge_data['status'] if charge_response else None
        # OpenPay error message
        suscription_payment.error_message = charge_data['error_message'] if charge_response else None
        suscription_payment.save()
        
        return Response({
                'suscription_name': suscription_payment.subscription_name,
                'amount': suscription_payment.amount,
                'order_id': suscription_payment.order_id
            }, status=status.HTTP_200_OK)

    def generate_order_recursively(self):
        already_exist_generated_order = True
        order_id = generateOrderString('SUB')
        while(already_exist_generated_order):
            try:
                Order.objects.get(order_id=order_id)
                already_exist_generated_order = True
                order_id = generateOrderString('SUB')
            except Order.DoesNotExist:
                already_exist_generated_order = False
        return order_id


class SubscriptionPaymentView(APIView):
    serializer_class = SubscriptionPaymentSerializer

    def get(self, request, order_id):
        try:
            payment = SubscriptionPayment.objects.filter(order_id=order_id)[0]
        except:
            return Response({'message': _('No se encontró el pago de la suscripción')}, status=status.HTTP_400_BAD_REQUEST)
        openpay_charge = None
        if payment.amount > 0:
            openpay_manager = OpenPayManager()
            openpay_charge = openpay_manager.get_charge(payment.openpay_id)
        return Response({
            'data': self.serializer_class(payment).data,
            'openpay': openpay_charge
        })
