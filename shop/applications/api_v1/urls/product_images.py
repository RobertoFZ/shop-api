from django.urls import path

from shop.applications.api_v1.views import product_images as product_images_views

urlpatterns = [
    # Category
    path('', product_images_views.ProductImagesListView.as_view()),
    path('<int:product_image_pk>/', product_images_views.ProductImageView.as_view()),
]
