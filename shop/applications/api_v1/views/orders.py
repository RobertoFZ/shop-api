from django.utils.translation import ugettext_lazy as _
from shop.settings import BUSINESS_NAME, URL_SERVER, OPEN_PAY_REDIRECT_URL, PAYPAL_API_URL, PAYPAL_API_CLIENT_ID, PAYPAL_API_CLIENT_SECRET

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination

from shop.applications.api_v1.serializers.orders import OrderSerializer
from shop.applications.api_v1.serializers.customers import CustomerSerializer
from shop.applications.api_v1.models import Business, Order, OrderProduct, Customer, ProductVariant, Product, ProductImage, User
from shop.applications.common.openpay import OpenPayManager
from shop.applications.common.functions import generateOrderString
from shop.applications.common.pagination import PaginationHandlerMixin

from shop.applications.common.functions import send_email
from django.template.loader import render_to_string
from shop.settings import URL_SERVER, EMAIL_CONTACT_FROM
from django.http import JsonResponse

import requests as HttpRequests


class OrdersView(APIView, PaginationHandlerMixin):

    def post(self, request):
        keys = request.data.keys()
        # We validates the request body structure
        if not 'products' in keys and not 'token_id' in keys and not 'customer' in keys and not 'device_id' in keys:
            return Response({'message': _('No se puede procesar la orden de compra.')}, status=status.HTTP_400_BAD_REQUEST)

        # We obtain products from request
        products = request.data['products']

        # We obtain the business ids from selected products
        business_ids = []
        for cart in products:
            product_variant = ProductVariant.objects.get(
                id=cart['product_variant_id'])

            if product_variant.use_stock and product_variant.stock < cart['quantity']:
                return Response({
                    'message': _('El producto %s %s no cuenta con stock. No se ha realizado el cobro de tu pedido.' % (product_variant.product.name, product_variant.name))
                }, status=status.HTTP_400_BAD_REQUEST)
            if not product_variant.product.business.id in business_ids:
                business_ids.append(product_variant.product.business.id)

        # Verify customer existance
        customer_verification = self.verify_customer(
            request.data['customer'], business_ids)
        if customer_verification['error']:
            return Response(customer_verification['data'], status=status.HTTP_400_BAD_REQUEST)

        # We generate the unique order id
        order_id = self.generate_order_recursively()
        # We obteain the paypment method
        payment_method = request.data['method']
        # We obtain the customer, device_id and token_id (OpenPay tokenization)
        customer = customer_verification['data']

        # We calculate the total amount
        total_amount = 0
        shipping_cost = 0
        for cart_product in products:
            try:
                product_variant = ProductVariant.objects.get(
                    id=cart_product['product_variant_id'])
                product_price = product_variant.price if not product_variant.price == None and not product_variant.price == 0 else product_variant.product.price
                product_shipping = product_variant.shipping_price if not product_variant.shipping_price == None and not product_variant.shipping_price == 0 else product_variant.product.shipping_price
                total_amount += product_price * cart_product['quantity']
                shipping_cost += product_shipping
                print(product_shipping)
            except ProductVariant.DoesNotExist:
                return Response({
                    'message': _('No se encontró la variante de producto con id %s.' % (cart_product['product_variant_id']))
                }, status=status.HTTP_400_BAD_REQUEST)
        openpay_charge_response = None

        if payment_method == 'openpay':
            token_id = request.data['token_id']
            device_id = request.data['device_id']

            openpay_charge_response = self.generate_openpay_charge(
                customer, token_id, device_id, total_amount, shipping_cost, order_id)

            if openpay_charge_response['error']:
                return Response({
                    'message': _('Ocurrió un problema al procesar tu pago, no se logró realizar el cargo.'),
                    'error': openpay_charge_response['data']
                }, status=status.HTTP_400_BAD_REQUEST)

        paypal_order = None
        if payment_method == 'paypal':
            paypal_token_request = HttpRequests.post("%s/v1/oauth2/token" % PAYPAL_API_URL, data={
                'grant_type': 'client_credentials'
            }, headers={'Content-type': 'application/x-www-form-urlencoded'}, auth=(PAYPAL_API_CLIENT_ID, PAYPAL_API_CLIENT_SECRET))
            paypal_token_response = paypal_token_request.json()

            paypal_order_request = HttpRequests.get(
                "%s/v2/checkout/orders/%s" % (PAYPAL_API_URL, request.data['paypal_order_id']), headers={
                    'Content-type': 'application/json',
                    'Authorization': "%s %s" % (paypal_token_response['token_type'], paypal_token_response['access_token'])
                })
            paypal_order = paypal_order_request.json()
            print(paypal_order)

        orders_array = []
        for business_id in business_ids:
            # We obtain the customer for the current business
            customer = list(filter(lambda customer: customer.business.id ==
                                   business_id, customer_verification['array']))[0]
            business = Business.objects.get(id=business_id)

            order = Order()
            # Assing relations
            order.customer = customer
            order.business = business
            # Assing attributes
            order.order_id = order_id
            # Processing status (This is a business logic status, not openpay status)
            order.status = 1
            # We set the amount here and in the OpenPay Charge request
            order.amount = round(total_amount, 2)
            order.shipping_cost = shipping_cost

            if payment_method == 'openpay':
                charge_data = openpay_charge_response['data']
                order.openpay_id = charge_data['id']  # OpenPay ID
                order.openpay_order_id = charge_data['order_id']
                # OpenPay bank authorization
                order.authorization = charge_data['authorization']
                # OpenPay status text
                order.openpay_status_text = charge_data['status']
                # OpenPay error message
                order.error_message = charge_data['error_message']
                order.method = 'openpay'
                print(openpay_charge_response['data'])
            if payment_method == 'paypal':
                order.paypal_order_id = paypal_order['id']
                order.method = 'paypal'
            order.save()

            # We filter cart by business id
            for cart in products:
                # Finding the product variant for assing relation
                product_variant = ProductVariant.objects.get(
                    id=cart['product_variant_id'])

                if product_variant.product.business.id == business.id:
                    # Creating model
                    order_product = OrderProduct()
                    # Assing relations
                    order_product.order = order
                    order_product.product_variant = product_variant
                    order_product.price = product_variant.price if not product_variant.price == None and not product_variant.price == 0 else product_variant.product.price
                    order_product.quantity = cart['quantity']
                    order_product.save()

                    # We update the current stock for the product if we need
                    if product_variant.use_stock:
                        product_variant.stock = product_variant.stock - \
                            cart['quantity']
                        product_variant.save()
            orders_array.append(order)
        # We serialize the order object
        order_serializer = OrderSerializer(orders_array, many=True)
        return Response({
            'data': order_serializer.data,
            'openpay_3d_secure_url': openpay_charge_response['data']['payment_method']['url'] if openpay_charge_response != None else None,
            'method': request.data['method'],
            'paypal_order': paypal_order['id'] if paypal_order != None else None
        }, status=status.HTTP_201_CREATED)

    def generate_openpay_charge(self, customer, token_id, device_id, total_amount, shipping_cost, order_id):
        open_pay_customer = {
            'name': customer['name'],
            'last_name': '',
            'phone_number': customer['phone'],
            'email': customer['email']
        }

        charge = {
            'customer': open_pay_customer,
            'method': 'card',
            'source_id': token_id,  # The OpenPay token resulting from frontend tokenization
            # We set the amount here and in the Order model
            'amount': round(total_amount + shipping_cost, 2),
            'currency': 'MXN',
            'description': "Compra en %s" % (BUSINESS_NAME),
            'order_id': order_id,
            'device_session_id': device_id,
            'use_3d_secure': True,
            'redirect_url': OPEN_PAY_REDIRECT_URL
        }

        # Initialize OpenPayManager
        openpay_manager = OpenPayManager()
        return openpay_manager.create_charge(charge)

    def verify_customer(self, customer_data, business_ids):
        customer_serializer = CustomerSerializer(
            data=customer_data)
        if customer_serializer.is_valid():
            customers = []
            for business_id in business_ids:
                customer = None
                business = Business.objects.get(id=business_id)
                try:
                    customer = Customer.objects.get(
                        email=customer_data['email'], business=business)
                except Customer.DoesNotExist:
                    pass
                if customer:
                    customer = customer_serializer.update(
                        customer, customer_serializer.validated_data)
                else:
                    customer_serializer.validated_data['business_id'] = business.id
                    customer = customer_serializer.create(
                        customer_serializer.validated_data, business)
                customers.append(customer)
            return {'error': False, 'data': customer_data, 'array': customers}
        return {'error': True, 'data': customer_serializer.errors}

    def generate_order_recursively(self):
        already_exist_generated_order = True
        order_id = generateOrderString('ORD')
        while(already_exist_generated_order):
            try:
                Order.objects.get(order_id=order_id)
                already_exist_generated_order = True
                order_id = generateOrderString('ORD')
            except Order.DoesNotExist:
                already_exist_generated_order = False
        return order_id


class OrdersListView(APIView, PaginationHandlerMixin):
    pagination_class = LimitOffsetPagination
    serializer_class = OrderSerializer

    def get(self, request, business_pk):
        try:
            business = Business.objects.get(id=business_pk)
        except Business.DoesNotExist:
            return Response({'message': _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)
        if not request.user.is_anonymous:
            orders = Order.objects.filter(
                business=business).order_by('-created_at')
        else:
            return Response({'message': _('No puedes realizar esta acción.')}, status=status.HTTP_401_UNAUTHORIZED)

        # We consult to openpay the order status
        openpay_manager = OpenPayManager()
        for order in orders:
            modified = False
            if order.method == 'openpay':
                openpay_manager = OpenPayManager()
                openpay_data = openpay_manager.get_charge(order.openpay_id)
                try:
                    if order.error_message != openpay_data['error_message']:
                        order.error_message = openpay_data['error_message']
                        modified = True
                except:
                    pass
                try:
                    if order.openpay_status_text != openpay_data['status']:
                        order.openpay_status_text = openpay_data['status']
                        modified = True
                except:
                    pass
                if modified:
                    order.save()

        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(
                page, many=True).data)
        else:
            serializer = self.serializer_class(orders, many=True)
        response = serializer.data
        return Response(response)


class OrderView(APIView):
    serializer_class = OrderSerializer

    def get(self, request, order_id):
        found = False
        try:
            order = Order.objects.filter(openpay_id=order_id)[0]
            found = True
        except:
            pass
        try:
            if not found:
                order = Order.objects.filter(paypal_order_id=order_id)[0]
        except:
            return Response({'message': _('No se encontró la orden')}, status=status.HTTP_400_BAD_REQUEST)

        openpay_charge = None
        if order.method == 'openpay':
            openpay_manager = OpenPayManager()
            openpay_charge = openpay_manager.get_charge(order.openpay_id)
        return Response({
            'data': self.serializer_class(order).data,
            'openpay': openpay_charge
        })


class TrackOrderView(APIView):
    serializer_class = OrderSerializer

    def get(self, request):
        try:
            order_id = request.query_params['order_id']
            order = Order.objects.filter(order_id=order_id)[0]
        except Order.DoesNotExist:
            return Response({'message': _('No se encontró la orden')}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'data': self.serializer_class(order).data
        })


class EmailConfirmOrder(APIView):

    def get_orders_ids(self, order):
        return order.id

    def post(self, request):

        try:
            # Email for Customer
            orders = Order.objects.filter(order_id=request.data['order_id'])
            customer = orders[0].customer

            orders_ids = list(map(self.get_orders_ids, orders))
            order_product = OrderProduct.objects.filter(
                order_id__in=orders_ids)

            data_order = {
                'orders': orders,
                'customer': customer,
                'order_product': order_product,
                'url_server': URL_SERVER,
            }
            to_order = [
                customer.email
            ]

            templete_path_order = 'emails/user_confirm_email.html'
            content_order = render_to_string(templete_path_order, data_order)
            title_order = "Correo de confirmación de compra"

            send_email(title_order, content_order,
                       to_order, content_type="text/html")

            # Email for Business
            for order in orders:
                user = User.objects.filter(id=order.business.users.all()[0].id)
                data_business = {
                    'order': order,
                    'url_server': URL_SERVER
                }

                if len(user) > 0:
                    email_business = user[0].email
                    to_business = [
                        email_business
                    ]

                templete_path_business = 'emails/business_confirm_email.html'
                content_business = render_to_string(
                    templete_path_business, data_business)
                title_business = "Correo de confirmación de venta"

                send_email(title_business, content_business,
                           to_business, content_type="text/html")

            return Response({'message': _('Los correos han sido enviados.')}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'message': _('Ocurrió un error al enviar el correo de confirmación.')}, status=status.HTTP_400_BAD_REQUEST)
