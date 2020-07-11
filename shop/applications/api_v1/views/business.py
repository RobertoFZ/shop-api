from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated

from shop.applications.api_v1.models import User, Business
from shop.settings import URL_SERVER
from shop.applications.api_v1.serializers.business import BusinessSerializer

# Create your views here.


class BusinessListView(APIView):
    serializer_class = BusinessSerializer

    def get(self, request):
        keys = request.query_params.keys()
        if 'admin' in keys and not request.user.is_anonymous or not request.user.is_anonymous:
            business = Business.objects.filter(users=request.user)
        else:
            business = Business.objects.filter(active=True)
        response = self.serializer_class(business, many=True).data
        return Response(response)

    def post(self, request):
        """
        Create a new Business
        :param request: Http request
        :return:
            - token: Auth token for the Business created
        """
        if request.user.is_anonymous:
            return Response({'message': _('No puedes realizar esta acción en estos momentos.')}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.serializer_class(data=request.data)

        try:
            business = Business.objects.filter(users=request.user)            
        except:            
            return Response({'message': _('No se encontraron negocios para este usuario.')}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(business) > 1:
            return Response({'message': _('Tu cuenta ha alcanzado el número máximo de negocios.')}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if serializer.is_valid():
                business = serializer.create(
                    serializer.validated_data, request.user)
                # Serializing business object
                response = self.serializer_class(business).data
                return Response(response, status=status.HTTP_201_CREATED)
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class BusinessView(APIView):
    """
    View for handle business actions
    """
    serializer_class = BusinessSerializer

    def get(self, request, business_pk):
        """
        Get the business data using Token authorization
        :param business_pk:
        :param request:
        :return:
        """
        try:
            business = Business.objects.filter(users__in=[request.user])
            #business = Business.objects.get(pk=business_pk, user=request.user)
        except Business.DoesNotExist:
            return Response({'message': _('Negocio no encontrado')}, status=status.HTTP_404_NOT_FOUND)

        if len(business) > 0:
            serializer = self.serializer_class(business[0])
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': _('Negocio no encontrado')}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, business_pk):
        """
        Handle the business data update
        :param business_pk:
        :param request:
        :return:
        """

        try:
            business = Business.objects.get(pk=business_pk)
        except Business.DoesNotExist:
            return Response({'message': _('Negocio no encontrado')}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            business = serializer.update(business, serializer.validated_data)
            serializer = self.serializer_class(business)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class BusinessUser(APIView):

    def post(self, request, business_pk):
        try:
            business = Business.objects.get(pk=business_pk)
        except Business.DoesNotExist:
            return Response({'message': _('Negocio no encontrado')}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = User.objects.get(pk=request.data['user_id'])
        except User.DoesNotExist:
            return Response({'message': _('Usuario no encontrado')}, status=status.HTTP_404_NOT_FOUND)

        try:
            business.users.add(user)
            business.save()
            return Response({'message': _('Usuario asignado al negocio')}, status=status.HTTP_200_OK)
        except:
            return Response({'message': _('Ocurrió un error al asignar al usuario')}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, business_pk):
        try:
            business = Business.objects.get(pk=business_pk)
        except Business.DoesNotExist:
            return Response({'message': _('Negocio no encontrado')}, status=status.HTTP_404_NOT_FOUND)

        try:
            user = User.objects.get(pk=request.data['user_id'])
        except User.DoesNotExist:
            return Response({'message': _('Usuario no encontrado')}, status=status.HTTP_404_NOT_FOUND)

        business.users.remove(user)
        business.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
