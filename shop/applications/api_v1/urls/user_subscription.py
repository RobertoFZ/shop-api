from django.urls import path

from shop.applications.api_v1.views import user_subscription as user_subscription_views

urlpatterns = [
    # User Subscriptions
    path('', user_subscription_views.UserSubscriptionCreate.as_view()),    
    path('<int:user_subscription_pk>/', user_subscription_views.UserSubscriptionView.as_view()),
]
