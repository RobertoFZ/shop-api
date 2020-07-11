from django.urls import path

from shop.applications.api_v1.views import business_settings as business_settings_views

urlpatterns = [
    # Business Settings
    path('', business_settings_views.BusinessSettingCreate.as_view()),
    path('<int:business_setting_pk>/', business_settings_views.BusinessSettingView.as_view()),
]