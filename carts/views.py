from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required


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
    current_user = request.user
    product = Product.objects.get(id=product_id)
    
    if current_user.is_authenticated:
        # this here is for the authenticated user
        product_variation = []
        
        
        # this here is a form which a user submits together variations
        if request.method == 'POST':
            # this here loops through what the user submits of variation and it made to key-value 
            
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                # this here is getting the variation submitted by the user/ the variation in our database
                
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass
        
        
        # this has been changed to if-else 
        # this here checks for an existing product with same variation in the cart
        
        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(user=current_user, product=product)
            # logic
            # existing variations -> database
            # current_variation -> product_variation
            # item_id -> database
            ex_var_list = []
            id = []
            # now we are going to check whether the variaton submitted by the user exists in our database, then we add the quantity without creating a new model
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
                
                
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                
                item.save()
            else:
                # if what us unside the list is greater than 0, then loop through the list
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                # this is saving the variation to the database table 'variation'
                    item.variations.add(*product_variation)
                # increase the quantity
                # cart_item.quantity += 1
                item.save()
        else:
            cart_item = CartItem.objects.create(product=product, quantity= 1, user=current_user)
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('carts:cart')
    
    # this here is the end for the authenticated user
    
    else:
        product_variation = []
        
        
        # this here is a form which a user submits together variations
        if request.method == 'POST':
            # this here loops through what the user submits of variation and it made to key-value 
            
            for item in request.POST:
                key = item
                value = request.POST[key]
                
                # this here is getting the variation submitted by the user/ the variation in our database
                
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
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
        
        
        
        # this has been changed to if-else 
        # this here checks for an existing product with same variation in the cart
        
        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(cart=cart, product=product)
            # logic
            # existing variations -> database
            # current_variation -> product_variation
            # item_id -> database
            ex_var_list = []
            id = []
            # now we are going to check whether the variaton submitted by the user exists in our database, then we add the quantity without creating a new model
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
                
                
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                
                item.save()
            else:
                # if what us unside the list is greater than 0, then loop through the list
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                # this is saving the variation to the database table 'variation'
                    item.variations.add(*product_variation)
                # increase the quantity
                # cart_item.quantity += 1
                item.save()
        else:
            cart_item = CartItem.objects.create(product=product, quantity= 1, cart=cart)
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('carts:cart')



# this here is for decrease what you have in the cart

def remove_cart(request, product_id, cart_item_id):
    
    product =get_object_or_404(Product, id=product_id)
    
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(user=request.user, product=product, id=cart_item_id)
            
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
            
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('carts:cart') 



def remove_cart_item(request, product_id, cart_item_id):
    product =get_object_or_404(Product, id=product_id)
    
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(user=request.user, product=product, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
    
    if cart_item.quantity:
        cart_item.delete()
    return redirect('carts:cart')

# if users are going to add products together with their cart_id, we need to pass it in the cart template, but it has to take three parameters, which are the total, quantity and cart_items=None
def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        
        
        # this here just checks if the user is authenticate, then whatever is in the cartitem template assign it to the userthat just logged in
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        
        else:
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




@login_required
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        # this here just checks if the user is authenticate, then whatever is in the cartitem template assign it to the userthat just logged in
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        
        else:
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
    return render(request, 'accounts/checkout.html', context)