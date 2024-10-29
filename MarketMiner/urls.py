from django.contrib import admin
from django.urls import path, include

from merchandise import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.brand_list, name='brand-list')
]
