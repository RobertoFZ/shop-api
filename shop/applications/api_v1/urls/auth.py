from django.urls import path

from shop.applications.api_v1.views import auth as auth_views

urlpatterns = [
    # Authentication
    path('login/', auth_views.AuthView.as_view()),
]
