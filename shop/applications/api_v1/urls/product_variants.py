from django.urls import path

from shop.applications.api_v1.views import product_variants as product_variants_views

urlpatterns = [
    # Category
    path('', product_variants_views.ProductsVariantListView.as_view()),
    path('<int:product_variant_pk>/',
         product_variants_views.ProductVariantView.as_view()),
]
