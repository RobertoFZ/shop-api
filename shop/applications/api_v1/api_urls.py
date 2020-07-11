from django.urls import path
from django.conf.urls import url, include
from shop.applications.api_v1.urls import users
from shop.applications.api_v1.urls import auth
from shop.applications.api_v1.urls import business
from shop.applications.api_v1.urls import client_products
from shop.applications.api_v1.urls import orders
from shop.applications.api_v1.urls import subscriptions
from shop.applications.api_v1.urls import contact
from shop.applications.api_v1.urls import review_purchases

urlpatterns = [
    # Users
    path('users/', include((users, 'users'))),
    path('auth/', include((auth, 'auth'))),
    path('business/', include((business, 'business'))),
    path('products/', include((client_products, 'client_products'))),
    path('orders/', include((orders, 'orders'))),
    path('subscriptions/', include((subscriptions, 'subscriptions'))),
    path('contact/', include((contact, 'contact'))),
    path('review_purchases/', include((review_purchases, 'review_purchases'))),
]
