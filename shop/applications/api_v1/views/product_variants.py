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
from shop.applications.api_v1.models import Business, Product, ProductVariant
from shop.settings import URL_SERVER
from shop.applications.api_v1.serializers.product_variants import ProductVariantSerializer


class ProductsVariantListView(APIView):
    serializer_class = ProductVariantSerializer

    def get(self, request, business_pk, product_pk):
        try:
            business = Business.objects.get(id=business_pk)
        except Business.DoesNotExit:
            return Response({'message', _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_pk)
        except Product.DoesNotExit:
            return Response({'message', _('No se encontró el producto.')}, status=status.HTTP_400_BAD_REQUEST)

        product_variants = ProductVariant.objects.filter(
            product__business=business, product=product)
        response = self.serializer_class(product_variants, many=True).data
        return Response(response)

    def post(self, request, business_pk, product_pk):
        try:
            Business.objects.get(id=business_pk)
        except Business.DoesNotExit:
            return Response({'message', _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_pk)
        except Product.DoesNotExit:
            return Response({'message', _('No se encontró el producto.')}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['product_id'] = product.id
            product_variants = serializer.create(
                serializer.validated_data, product)
            response = self.serializer_class(product_variants).data
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class ProductVariantView(APIView):
    serializer_class = ProductVariantSerializer

    def get(self, request, business_pk, product_pk, product_variant_pk):
        try:
            Business.objects.get(id=business_pk)
        except Business.DoesNotExist:
            return Response({'message', _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_pk)
        except Product.DoesNotExist:
            return Response({'message', _('No se encontró el producto.')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product_variant = ProductVariant.objects.get(
                id=product_variant_pk, deleted_at=None)
        except ProductVariant.DoesNotExist:
            return Response({'message', _('No se encontró la variante del producto.')}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(product_variant)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, business_pk, product_pk, product_variant_pk):
        try:
            Business.objects.get(id=business_pk)
        except Business.DoesNotExist:
            return Response({'message', _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_pk)
        except Product.DoesNotExist:
            return Response({'message', _('No se encontró el producto.')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product_variant = ProductVariant.objects.get(id=product_variant_pk)
        except ProductVariant.DoesNotExist:
            return Response({'message', _('No se encontró la variante del producto.')}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            product = serializer.update(
                product_variant, serializer.validated_data)
            serializer = self.serializer_class(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, business_pk, product_pk, product_variant_pk):
        try:
            Business.objects.get(id=business_pk)
        except Business.DoesNotExist:
            return Response({'message', _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_pk)
        except Product.DoesNotExist:
            return Response({'message', _('No se encontró el producto.')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product_variant = ProductVariant.objects.get(id=product_variant_pk)
        except ProductVariant.DoesNotExist:
            return Response({'message', _('No se encontró la variante del producto.')}, status=status.HTTP_400_BAD_REQUEST)

        product_variant.deleted_at = timezone.now()
        product_variant.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
