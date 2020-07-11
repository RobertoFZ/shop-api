from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated

from shop.applications.api_v1.models import User, Business, Category, Product
from shop.settings import URL_SERVER
from shop.applications.api_v1.serializers.categories import CategoriesSerializer


class CategoryListView(APIView):
    serializer_class = CategoriesSerializer

    def get(self, request, business_pk):
        try:
            business = Business.objects.get(id=business_pk)
        except Business.DoesNotExist:
            return Response({'message': _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)

        categories = Category.objects.filter(business=business)
        response = self.serializer_class(categories, many=True).data
        return Response(response)

    def post(self, request, business_pk):
        if request.user.is_anonymous:
            return Response({'message': _('No puedes realizar esta acción en estos momentos.')}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            business = Business.objects.get(id=business_pk)
        except Business.DoesNotExist:
            return Response({'message': _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['business_id'] = business.id
            categories = serializer.create(serializer.validated_data, business)
            response = self.serializer_class(categories).data
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class CategoryView(APIView):
    serializer_class = CategoriesSerializer

    def get(self, request, business_pk, category_pk):
        try:
            business = Business.objects.get(id=business_pk)
        except Business.DoesNotExits:
            return Response({'message': _('No se encontró el negocio.')}, status=status.HTTP_404_NOT_FOUND)

        try:
            category = Category.objects.get(id=category_pk)
        except Category.DoesNotExist:
            return Response({'message': _('No se encontró la categoria.')}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(category)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, business_pk, category_pk):
        try:
            business = Business.objects.get(id=business_pk)
        except Business.DoesNotExit:
            return Response({'message': _('No se encontró el negocio.')}, status=status.HTTP_404_NOT_FOUND)

        try:
            category = Category.objects.get(id=category_pk)
        except Category.DoesNotExit:
            return Response({'message': _('No se encontró la categoria.')}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            category = serializer.update(category, serializer.validated_data)
            serializer = self.serializer_class(category)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, business_pk, category_pk):
        try:
            business = Business.objects.get(id=business_pk)
        except Business.DoesNotExit:
            return Response({'message': _('No se encontró el negocio.')}, status=status.HTTP_404_NOT_FOUND)

        try:
            category = Category.objects.get(id=category_pk)
        except Category.DoesNotExit:
            return Response({'message': _('No se encontró la categoria.')}, status=status.HTTP_404_NOT_FOUND)

        products = Product.objects.filter(
            subcategory__category=category).count()

        if products > 0:
            return Response({'message': _('La categoría contiene subcategorías asignadas a productos, no puedes eliminarla.')}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if category.image:
                category.image.delete()
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
