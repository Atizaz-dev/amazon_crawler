from django.shortcuts import render
from django.db.models import Q

from .models import Brand, Product


def brand_list(request):
    search_query = request.GET.get('search', '')
    brands = Brand.objects.all()

    if search_query:
        products = Product.objects.filter(Q(name__icontains=search_query) | Q(asin__icontains=search_query))
    else:
        products = Product.objects.all()

    context = {
        'brands': brands,
        'products': products,
        'search_query': search_query,
    }
    return render(request, 'home.html', context)
