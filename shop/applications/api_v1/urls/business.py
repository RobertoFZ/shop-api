from django.urls import path

from shop.applications.api_v1.views import business as business_views
from shop.applications.api_v1.views import subcategories as subcategories_views
from shop.applications.api_v1.views import orders as orders_views
from shop.applications.api_v1.views import customers as customers_views
from shop.applications.api_v1.urls import categories, collections
from shop.applications.api_v1.urls import products
from shop.applications.api_v1.urls import business_settings
from django.conf.urls import url, include
urlpatterns = [
    # Business
    path('', business_views.BusinessListView.as_view()),
    path('<int:business_pk>/', business_views.BusinessView.as_view()),
    path('<int:business_pk>/users', business_views.BusinessUser.as_view()),
    path('<int:business_pk>/categories/', include((categories, 'categories'))),
    path('<int:business_pk>/collections/',
         include((collections, 'collections'))),
    path('<int:business_pk>/subcategories/',
         subcategories_views.SubCategoryListAllView.as_view()),
    path('<int:business_pk>/products/', include((products, 'products'))),
    path('<int:business_pk>/business_settings/', include((business_settings, 'business_settings'))),
    path('<int:business_pk>/orders/', orders_views.OrdersListView.as_view()),
    path('<int:business_pk>/customers/',
         customers_views.CustomerListView.as_view()),         
]
