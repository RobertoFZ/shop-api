from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated

from shop.applications.api_v1.models import Business, Category, SubCategory, Product
from shop.settings import URL_SERVER
from shop.applications.api_v1.serializers.subcategories import SubCategoriesSerializer


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class SubCategoryListAllView(APIView):
    serializer_class = SubCategoriesSerializer

    def get(self, request, business_pk):
        try:
            business = Business.objects.get(id=business_pk)
        except Business.DoesNotExist:
            return Response({'message': _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)

        subcategories = SubCategory.objects.filter(category__business=business)
        response = self.serializer_class(subcategories, many=True).data
        return Response(response)


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class SubCategoryListView(APIView):
    serializer_class = SubCategoriesSerializer

    def get(self, request, business_pk, category_pk):
        try:
            business = Business.objects.get(id=business_pk)
        except Business.DoesNotExist:
            return Response({'message': _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Category.objects.get(id=category_pk)
        except Category.DoesNotExist:
            return Response({'message', _('No se encontró la categoria')}, status=status.HTTP_400_BAD_REQUEST)

        subcategories = SubCategory.objects.filter(category=category)
        response = self.serializer_class(subcategories, many=True).data
        return Response(response)

    def post(self, request, business_pk, category_pk):
        try:
            business = Business.objects.get(id=business_pk)
        except Business.DoesNotExist:
            return Response({'message': _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Category.objects.get(id=category_pk)
        except Category.DoesNotExist:
            return Response({'message', _('No se encontró la categoria')}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['category_id'] = category.id
            subcategories = serializer.create(
                serializer.validated_data, category)
            response = self.serializer_class(subcategories).data
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class SubCategoryView(APIView):
    serializer_class = SubCategoriesSerializer

    def get(self, request, business_pk, category_pk, subcategory_pk):
        try:
            business = Business.objects.get(id=business_pk)
        except Business.DoesNotExits:
            return Response({'message': _('No se encontró el negocio.')}, status=status.HTTP_404_NOT_FOUND)

        try:
            category = Category.objects.get(id=category_pk)
        except Category.DoesNotExist:
            return Response({'message': _('No se encontró la categoria.')}, status=status.HTTP_404_NOT_FOUND)

        try:
            subcategory = SubCategory.objects.get(id=subcategory_pk)
        except SubCategory.DoesNotExist:
            return Response({'message': _('No se encontró la subcategoria')}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(subcategory)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, business_pk, category_pk, subcategory_pk):
        try:
            business = Business.objects.get(id=business_pk)
        except Business.DoesNotExit:
            return Response({'message': _('No se encontró el negocio.')}, status=status.HTTP_404_NOT_FOUND)

        try:
            category = Category.objects.get(id=category_pk)
        except Category.DoesNotExit:
            return Response({'message': _('No se encontró la categoria.')}, status=status.HTTP_404_NOT_FOUND)

        try:
            subcategory = SubCategory.objects.get(id=subcategory_pk)
        except SubCategory.DoesNotExist:
            return Response({'message': _('No se encontró la subcategoria.')}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            subcategory = serializer.update(
                subcategory, serializer.validated_data)
            serializer = self.serializer_class(subcategory)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, business_pk, category_pk, subcategory_pk):
        try:
            business = Business.objects.get(id=business_pk)
        except Business.DoesNotExit:
            return Response({'message': _('No se encontró el negocio.')}, status=status.HTTP_404_NOT_FOUND)

        try:
            category = Category.objects.get(id=category_pk)
        except Category.DoesNotExit:
            return Response({'message': _('No se encontró la categoria.')}, status=status.HTTP_404_NOT_FOUND)

        try:
            subcategory = SubCategory.objects.get(id=subcategory_pk)
        except SubCategory.DoesNotExist:
            return Response({'message': _('No se encontró la subcategoria.')}, status=status.HTTP_404_NOT_FOUND)

        products = Product.objects.filter(
            subcategory=subcategory).count()

        if products > 0:
            return Response({'message': _('La subcategoría se encuentra asignada a %s productos, no puedes eliminarla.' % products)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if subcategory.image:
                subcategory.image.delete()
            subcategory.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
