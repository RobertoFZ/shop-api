from django.urls import path

from shop.applications.api_v1.views import review_purchases as review_purchase_views

urlpatterns = [
    # Review Purchase
    path('', review_purchase_views.ReviewPurchaseListView.as_view()),    
    path('<int:review_purchase_pk>/', review_purchase_views.ReviewPurchaseView.as_view()),    
]
