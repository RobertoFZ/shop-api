from django.urls import path

from shop.applications.api_v1.views import products as products_views
from shop.applications.api_v1.urls import product_images as product_images_views
from shop.applications.api_v1.urls import product_variants as product_variants_views
from django.conf.urls import url, include

urlpatterns = [
    # Category
    path('', products_views.ProductsListView.as_view()),
    path('<int:product_pk>/', products_views.ProductView.as_view()),
    path('<int:product_pk>/product_images/',
         include((product_images_views, 'product_images'))),
    path('<int:product_pk>/product_variants/',
         include((product_variants_views, 'product_variants'))),
]
