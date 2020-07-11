from django.urls import path

from shop.applications.api_v1.views import categories as categories_views
from django.conf.urls import url, include
from shop.applications.api_v1.urls import subcategories

urlpatterns = [
    # Category
    path('', categories_views.CategoryListView.as_view()),
    path('<int:category_pk>/', categories_views.CategoryView.as_view()),
    path('<int:category_pk>/subcategories/', include((subcategories, 'subcategories'))),
]
