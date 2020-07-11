from django.urls import path

from shop.applications.api_v1.views import users as users_views
from django.conf.urls import url, include
from shop.applications.api_v1.urls import user_subscription

urlpatterns = [
    # Authentication
    path('', users_views.UsersView.as_view()),
    path('<int:user_pk>/', users_views.UserView.as_view()),
    path('<int:user_pk>/user_subscription/', include((user_subscription, 'user_subscription'))),
]
