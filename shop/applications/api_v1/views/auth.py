from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer

from shop.applications.api_v1.models import User, Profile
from shop.settings import URL_SERVER
from shop.applications.api_v1.serializers.users import UserSerializer

# Create your views here.

class AuthView(APIView):
    """
    View for authenticate user
    """
    serializer_class = AuthTokenSerializer

    def post(self, request):
        """
        Method for obtain user token and user data
        :param request: Http request
        :return: The user data with token included
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            # We dont need do something with the token created, the serializers handle it
            user.profile = Profile.objects.get(user=user)
            response = UserSerializer(user).data
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {
                'message': _("Correo o contraseña incorrecta"),
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
