from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated

from shop.applications.api_v1.models import User, Business, Collection
from shop.settings import URL_SERVER
from shop.applications.api_v1.serializers.collections import CollectionsSerializer

class CollectionListView(APIView):
    serializer_class = CollectionsSerializer

    def get(self, request, business_pk):
        try:
            business = Business.objects.get(id = business_pk)
        except Business.DoesNotExist:
            return Response({'message': _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)
        
        collections = Collection.objects.filter(business = business)
        response = self.serializer_class(collections, many=True).data
        return Response(response)
    
    def post(self, request, business_pk):
        try:
            business = Business.objects.get(id = business_pk)
        except Business.DoesNotExist:
            return Response({'message': _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.serializer_class(data = request.data)
        if serializer.is_valid():
            collections = serializer.create(serializer.validated_data, business)
            response = self.serializer_class(collections).data
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class CollectionsView(APIView):
    serializer_class = CollectionsSerializer

    def get(self, request, business_pk, collection_pk):
        try:
            business = Business.objects.get(id = business_pk)
        except Business.DoesNotExist:
            return Response({'message': _('No encontró el negocio.')}, status=status.HTTP_404_NOT_FOUND)

        try:
            collection = Collection.objects.get(id = collection_pk)
        except Collection.DoesNotExist:
            return Response({'message': _('No se encontró la collección.')}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(collection)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, business_pk, collection_pk):
        try: 
            business = Business.objects.get(id = business_pk)
        except Business.DoesNotExist:
            return Response({'message': _('No se encontró el negocio.')}, status=status.HTTP_404_NOT_FOUND)

        try:
            collection = Collection.objects.get(id = collection_pk)
        except Collection.DoesNotExist:
            return Response({'message': _('No sé encontró la colleción')}, status=status.HTTP_4004_NOT_FOUND)

        serializer = self.serializer_class(data = request.data)

        if serializer.is_valid():
            collection = serializer.update(collection, serializer.validated_data)
            serializer = self.serializer_class(collection)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, business_pk, collection_pk):
        try:
            business = Business.objects.get(id = business_pk)
        except Business.DoesNotExist:
            return Response({'message': _('No encontró el negocio.')}, status=status.HTTP_404_NOT_FOUND)

        try:
            collection = Collection.objects.get(id = collection_pk)
        except Collection.DoesNotExist:
            return Response({'message': _('No se encontró la collección.')}, status=status.HTTP_404_NOT_FOUND)
        
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)