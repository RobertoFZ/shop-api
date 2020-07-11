from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated

from shop.applications.api_v1.models import Business, Product, ProductImage
from shop.settings import URL_SERVER
from shop.applications.api_v1.serializers.product_images import ProductImageSerializer


class ProductImagesListView(APIView):
    serializer_class = ProductImageSerializer

    def get(self, request, business_pk, product_pk):
        try:
            Business.objects.get(id=business_pk)
        except Business.DoesNotExist:
            return Response({'message', _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_pk)
        except Product.DoesNotExit:
            return Response({'message', _('No se encontró el producto.')}, status=status.HTTP_400_BAD_REQUEST)

        product_images = ProductImage.objects.filter(product=product)
        response = self.serializer_class(product_images, many=True).data
        return Response(response)

    def post(self, request, business_pk, product_pk):
        try:
            product = Product.objects.get(id=product_pk)
        except Product.DoesNotExit:
            return Response({'message', _('No se encontró el producto.')}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['product_id'] = product.id
            product_image = serializer.create(
                serializer.validated_data, product)
            response = self.serializer_class(product_image).data
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class ProductImageView(APIView):
    def delete(self, request, business_pk, product_pk, product_image_pk):
        try:
            Business.objects.get(id=business_pk)
        except Business.DoesNotExist:
            return Response({'message', _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            Product.objects.get(id=product_pk)
        except Product.DoesNotExist:
            return Response({'message', _('No se encontró el producto.')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product_image = ProductImage.objects.get(id=product_image_pk)
        except ProductImage.DoesNotExist:
            return Response({'message', _('No se encontró la imagen del producto.')}, status=status.HTTP_400_BAD_REQUEST)
        product_image.image.delete()
        product_image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
