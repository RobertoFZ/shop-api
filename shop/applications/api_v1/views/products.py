from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db.models import Q

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from datetime import datetime

from shop.applications.common.pagination import PaginationHandlerMixin
from shop.applications.api_v1.models import Business, Product
from shop.settings import URL_SERVER
from shop.applications.api_v1.serializers.products import ProductSerializer, ProductDataSerializer


class AllProductsListView(APIView, PaginationHandlerMixin):
    """
    This View is for the client shop application (For list all products without the business)
    Allow filters product by category (If business is present), business and order by price
    """
    serializer_class = ProductDataSerializer
    pagination_class = LimitOffsetPagination

    def get(self, request):
        categories = business = order = None
        keys = request.query_params.keys()
        products = []
        if 'category' in keys:
            categories = request.query_params['category'].split(',')
        if 'business' in keys:
            business = request.query_params['business'].split(',')
        if 'order' in keys and request.query_params['order'] in ['asc', 'desc']:
            order = request.query_params['order']

        if categories and business:
            products = Product.objects.filter(
                Q(publish_at__lte=datetime.now()) | Q(published=True)).filter(deleted_at=None).filter(
                subcategory__category__pk__in=categories, business__pk__in=business, business__active=True).exclude(subcategory=None)
        elif categories and not business:
            products = Product.objects.filter(
                Q(publish_at__lte=datetime.now()) | Q(published=True)).filter(deleted_at=None).filter(
                subcategory__category__pk__in=categories, business__active=True)
        elif business and not categories:
            products = Product.objects.filter(
                Q(publish_at__lte=datetime.now()) | Q(published=True)).filter(deleted_at=None).filter(
                business__pk__in=business, business__active=True)
        else:
            products = Product.objects.filter(
                Q(publish_at__lte=datetime.now()) | Q(published=True)).filter(deleted_at=None, business__active=True)
        if order:
            products = (products.order_by(
                '-price') if order == 'desc' else products.order_by('price'))

        page = self.paginate_queryset(products)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(
                page, many=True).data)
        else:
            serializer = self.serializer_class(products, many=True)
        response = serializer.data
        return Response(response)


class ProductDataView(APIView):
    """
    This method is used to retrive information about a product for shop client without authentication
    """
    serializer_class = ProductDataSerializer

    def get(self, request, product_pk):
        try:
            product = Product.objects.get(id=product_pk)
        except Product.DoesNotExist:
            return Response({'message', _('No se encontró el producto.')}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(product)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductsListView(APIView):
    serializer_class = ProductSerializer
    serializer_class_data = ProductDataSerializer

    def get(self, request, business_pk):
        try:
            business = Business.objects.get(id=business_pk)
        except Business.DoesNotExit:
            return Response({'message', _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)

        products = Product.objects.filter(
            business=business, published=True).exclude(publish_at__gte=timezone.now())
        response = self.serializer_class_data(products, many=True).data
        return Response(response)

    def post(self, request, business_pk):
        try:
            business = Business.objects.get(id=business_pk)
        except Business.DoesNotExit:
            return Response({'message', _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            products = Product.objects.filter(business_id=business_pk, published=True)            
        except:            
            return Response({'message', _('No se encontraron productos para este negocio.')}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(products) > 3:
            return Response({'message', _('Tu cuenta ha alcanzado el número máximo de productos.')}, status=status.HTTP_400_BAD_REQUEST)
        else:                        
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                try:
                    timestamp = serializer.validated_data['publish_at']
                    serializer.validated_data['publish_at'] = datetime.fromtimestamp(
                        timestamp)
                except:
                    pass
                serializer.validated_data['business_id'] = business.id
                products = serializer.create(serializer.validated_data, business)
                response = self.serializer_class_data(products).data
                return Response(response, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class ProductView(APIView):
    serializer_class = ProductSerializer
    serializer_class_data = ProductDataSerializer

    def get(self, request, business_pk, product_pk):
        try:
            Business.objects.get(id=business_pk)
        except Business.DoesNotExist:
            return Response({'message', _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_pk)
        except Product.DoesNotExist:
            return Response({'message', _('No se encontró el producto.')}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class_data(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, business_pk, product_pk):
        try:
            Business.objects.get(id=business_pk)
        except Business.DoesNotExist:
            return Response({'message', _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_pk)
        except Product.DoesNotExist:
            return Response({'message', _('No se encontró el producto.')}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                timestamp = serializer.validated_data['publish_at']
                serializer.validated_data['publish_at'] = datetime.fromtimestamp(
                    timestamp)
            except:
                product = serializer.update(product, serializer.validated_data)
                serializer = self.serializer_class_data(product)
                return Response(serializer.data, status=status.HTTP_200_OK)

            product = serializer.update(product, serializer.validated_data)
            serializer = self.serializer_class_data(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, business_pk, product_pk):
        try:
            Business.objects.get(id=business_pk)
        except Business.DoesNotExist:
            return Response({'message', _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_pk)
        except Product.DoesNotExist:
            return Response({'message', _('No se encontró el producto.')}, status=status.HTTP_400_BAD_REQUEST)

        product.deleted_at = timezone.now()
        product.published = False
        product.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
