from django.urls import path

from shop.applications.api_v1.views import subcategories as subcategories_views

urlpatterns = [
    # SubCategory
    path('', subcategories_views.SubCategoryListView.as_view()),
    path('<int:subcategory_pk>/', subcategories_views.SubCategoryView.as_view()),
    
]
