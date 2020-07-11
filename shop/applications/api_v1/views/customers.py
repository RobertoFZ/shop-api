from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination

from shop.applications.api_v1.serializers.customers import CustomerSerializer
from shop.applications.api_v1.models import Business, Customer
from shop.applications.common.pagination import PaginationHandlerMixin


@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class CustomerListView(APIView, PaginationHandlerMixin):
    pagination_class = LimitOffsetPagination
    serializer_class = CustomerSerializer

    def get(self, request, business_pk):
        try:
            business = Business.objects.get(id=business_pk)
        except Business.DoesNotExist:
            return Response({'message': _('No se encontró el negocio.')}, status=status.HTTP_400_BAD_REQUEST)
        customers = Customer.objects.filter(business=business)

        page = self.paginate_queryset(customers)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(
                page, many=True).data)
        else:
            serializer = self.serializer_class(customers, many=True)
        response = serializer.data
        return Response(response)
