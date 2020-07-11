from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

from shop.applications.common.functions import send_email
from django.template.loader import render_to_string
from shop.settings import URL_SERVER, EMAIL_CONTACT_FROM

class ContactView(APIView):

    def validate(self, data):    
        if not data['name']:
            return False
        if not data['email']:
            return False
        if not data['phone']:
            return False
        if not data['message']:
            return False
        else:
            return True

    def post(self, request):                     
        if self.validate(request.data):            
            try:                                
                data = {
                    'contact': request.data,
                    'url_server': URL_SERVER,            
                }
                to = [
                    EMAIL_CONTACT_FROM
                ]                                

                templete_path = 'emails/contact.html'
                content = render_to_string(templete_path, data)
                title="Contacto Arca de Troya"

                send_email(title, content, to, content_type="text/html")

                return Response({'message': _('El correo ha sido enviado.')}, status=status.HTTP_200_OK)
            except:
                return Response({'message': _('El correo no se ha podido enviar.')}, status=status.HTTP_400_BAD_REQUEST)
                                    
        else:
            return Response({'message': _('Datos incompletos, favor de completar la información.')}, status=status.HTTP_400_BAD_REQUEST)


    