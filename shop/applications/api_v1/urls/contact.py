from django.urls import path

from shop.applications.api_v1.views import contact as contact_view

urlpatterns = [    
    path('', contact_view.ContactView.as_view()),
]