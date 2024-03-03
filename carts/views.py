from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from .models import *
from store.models import *
# Create your views here.



# This views here get/creates session key for each user, and after that, it checks if product is in cart, then it should increase the quantity

# this function gets the session key
def _cart_id(request):
    cart = request.session.session_key
    # if the user doesn't have session key, then it should create one for them
    if not cart:
        cart = request.session.create()
    return cart



# this function here is what adds the product and the session key to the cart

def add_cart(request, product_id):
    # firt we have to get the product
    product = Product.objects.get(id=product_id)
    product_variation = []
    
    
    # this here is a form which a user submits together variations
    if request.method == 'POST':
        # this here loops through what the user submits of variation and it made to key-value 
        
        for item in request.POST:
            key = item
            value = request.POST[key]
            
            # this here is getting the variation submitted by the user/ the variation in our database
            
            try:
                variation = Variation.objects.get(product=product, variation_category=key, variation_value=value)
                product_variation.append(variation)
            except:
                pass
    
    
    # getting the cart id
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save()
    
    # trying for the cart item now
    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        # increase the quantity
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(product=product, quantity= 1, cart=cart)
        cart_item.save()
    return redirect('carts:cart')



# this here is for decrease what you have in the cart

def remove_cart(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product =get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(cart=cart, product=product)
        
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('carts:cart') 

def remove_cart_item(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product =get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(cart=cart, product=product)
    
    if cart_item.quantity:
        cart_item.delete()
    return redirect('carts:cart')

# if users are going to add products together with their cart_id, we need to pass it in the cart template, but it has to take three parameters, which are the total, quantity and cart_items=None
def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        # here we are going to loop through the stuffs we just got, then increase their quantity. together with total
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass
    
    context = {
        'tax': tax,
        'grand_total': grand_total,
        'cart_items': cart_items,
        'total':total,
        'quantity':quantity,
    }
    return render(request, 'carts/cart.html',context)