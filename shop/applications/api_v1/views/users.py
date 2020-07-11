from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

from shop.applications.api_v1.models import User, Profile
from shop.settings import URL_SERVER
from shop.applications.api_v1.serializers.users import UserSerializer

# Create your views here.


class UsersView(APIView):
    serializer_class = UserSerializer

    def post(self, request):
        """
        Create a new user
        :param request: Http request
        :return:
            - token: Auth token for the user created
        """
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = serializer.create(serializer.validated_data)

            # Send welcome email
            data = {
                'user': user,
                'url_server': URL_SERVER,
            }
            user.send_email(template_path='emails/new_user.html',
                            title='Registro en Arca de Troya', data=data)

            # Token creation
            token, created = Token.objects.get_or_create(user=user)

            # Serializing user object
            response = self.serializer_class(user).data

            return Response(response, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class UserView(APIView):
    """
    View for handle account creation
    """
    serializer_class = UserSerializer

    def get(self, request, user_pk):
        """
        Get the account data using Token authorization
        :param user_pk:
        :param request:
        :return:
        """
        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            return Response({'message': _('Usuario no encontrado')}, status=status.HTTP_404_NOT_FOUND)

        if request.user == user:
            user.profile = Profile.objects.get(user=user)
            serializer = self.serializer_class(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'message': _('No tienes permisos para realizar está acción')},
                            status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, user_pk):
        """
        Handle the account data update
        :param user_pk:
        :param request:
        :return:
        """

        try:
            user = User.objects.get(pk=user_pk)
        except User.DoesNotExist:
            return Response({'message': _('Usuario no encontrado')}, status=status.HTTP_404_NOT_FOUND)

        if request.user != user:
            return Response({'message': _('No tienes permisos para realizar está acción')},
                            status=status.HTTP_401_UNAUTHORIZED)

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user.profile = Profile.objects.get(user=user)
            user = serializer.update(user, serializer.validated_data)
            serializer = self.serializer_class(user)

            token, created = Token.objects.get_or_create(user=request.user)

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
