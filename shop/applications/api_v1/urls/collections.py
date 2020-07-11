from django.urls import path

from shop.applications.api_v1.views import collections as collections_views

urlpatterns = [
    #Colletion
    path('', collections_views.CollectionListView.as_view()),
    path('<int:collection_pk>/', collections_views.CollectionsView.as_view()),
]