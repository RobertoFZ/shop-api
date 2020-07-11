from django.urls import path

from shop.applications.api_v1.views import orders as orders_views
from django.conf.urls import url, include
urlpatterns = [
    # Orders
    path('', orders_views.OrdersView.as_view()),
    path('email/', orders_views.EmailConfirmOrder.as_view()),
    path('track/', orders_views.TrackOrderView.as_view()),
    path('<str:order_id>/', orders_views.OrderView.as_view()),
]
