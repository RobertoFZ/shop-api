from django.utils.translation import ugettext_lazy as _

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated

from shop.applications.api_v1.models import ReviewPurchase, ProductVariant
from shop.settings import URL_SERVER
from shop.applications.api_v1.serializers.review_purchases import ReviewPurchaseSerializer

class ReviewPurchaseListView(APIView):
    serializer_class = ReviewPurchaseSerializer

    def get(self, request):
          
        if request.query_params['product_id']:
            review_purchase = ReviewPurchase.objects.filter(product_variant__product__id=request.query_params['product_id']).order_by('-created_at')               
        else:           
            review_purchase = ReviewPurchase.objects.all().order_by('-created_at')                                  
        response = self.serializer_class(review_purchase, many=True).data
        return Response(response)
    
    def post(self, request):
        try:
            product_variant = ProductVariant.objects.get(id=request.data['product_variant_id'])
        except ProductVariant.DoesNotExist:
            return Response({'message', _('No se encontró la variante del producto.')}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            review_purchase = serializer.create(serializer.validated_data, product_variant)
            response = self.serializer_class(review_purchase).data
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@authentication_classes((TokenAuthentication,))
@permission_classes((IsAuthenticated,))
class ReviewPurchaseView(APIView):
    serializer_class = ReviewPurchaseSerializer

    def get(self, request, review_purchase_pk):        
        try:
            review_purchase = ReviewPurchase.objects.get(id=review_purchase_pk)
        except ReviewPurchase.DoesNotExist:
            return Response({'message', _('No se encontró el comentario.')}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(review_purchase)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, review_purchase_pk):        
        try:
            review_purchase = ReviewPurchase.objects.get(id=review_purchase_pk)
        except ReviewPurchase.DoesNotExist:
            return Response({'message', _('No se encontró el comentario.')}, status=status.HTTP_400_BAD_REQUEST)
        
        review_purchase.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)