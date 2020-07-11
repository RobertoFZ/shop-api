from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated

from shop.applications.api_v1.models import BusinessSetting, Business
from shop.settings import URL_SERVER
from shop.applications.api_v1.serializers.business_settings import BussinesSettingSerializer

@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class BusinessSettingCreate(APIView):
    serializer_class = BussinesSettingSerializer

    def post(self, request, business_pk):
        try:
            business = Business.objects.get(id=business_pk)
        except Business.DoesNotExist:
            return Response({'message': _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            business_setting = serializer.create(serializer.validated_data, business)
            response = self.serializer_class(business_setting).data
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class BusinessSettingView(APIView):
    serializer_class = BussinesSettingSerializer

    def get(self, request, business_pk, business_setting_pk):
        try:
            business = Business.objects.get(id=business_pk)
        except Business.DoesNotExist:
            return Response({'message': _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.serializer_class(data=request.data)

        try:
            business_setting = BusinessSetting.objects.get(id=business_setting_pk)
        except BusinessSetting.DoesNotExist:
            return Response({'message': _('No se encontró la configuración del negocio.')}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(business_setting)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, business_pk, business_setting_pk):
        try:
            business = Business.objects.get(id=business_pk)
        except Business.DoesNotExist:
            return Response({'message': _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.serializer_class(data=request.data)

        try:
            business_setting = BusinessSetting.objects.get(id=business_setting_pk)
        except BusinessSetting.DoesNotExist:
            return Response({'message': _('No se encontró la configuración del negocio.')}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            business_setting = serializer.update(business_setting, serializer.validated_data)
            serializer = self.serializer_class(business_setting)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
