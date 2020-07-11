from django.urls import path

from shop.applications.api_v1.views import subscriptions as subscriptions_views

urlpatterns = [
    # subscriptions
    path('', subscriptions_views.SubscriptionListView.as_view()),
    path('<int:subscription_pk>/', subscriptions_views.SubscriptionView.as_view()),
]
