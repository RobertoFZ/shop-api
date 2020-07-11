from django.urls import path

from shop.applications.api_v1.views import products as products_views
from django.conf.urls import url, include

urlpatterns = [
    # All Products
    path('', products_views.AllProductsListView.as_view()),
    # One Product
    path('<int:product_pk>', products_views.ProductDataView.as_view()),
]
