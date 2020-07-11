from django.contrib import admin
from shop.applications.api_v1.models import AppVersion, Business, User, Category

# Register your models here.
admin.site.register(AppVersion)
admin.site.register(User)
admin.site.register(Business)
admin.site.register(Category)