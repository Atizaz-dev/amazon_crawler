from django.contrib import admin

from .models import Brand, Product


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'asin', 'brand']
    search_fields = ['name', 'asin']
    list_filter = ['brand']
