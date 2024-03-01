from django.shortcuts import render

from store.models import *

# Create your views here.
def index(request):
    products = Product.objects.all().filter(is_available=True)
    
    context = {
        'products': products,
    }
    return render(request, 'category/index.html', context)