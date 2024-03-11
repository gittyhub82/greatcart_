from django.shortcuts import render, redirect
import datetime
import json
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

from .forms import *
from carts.models import *
from .models import Payment, OrderProduct, Order
from store.models import Product
# Create your views here.


def place_order(request, total=0, quantity=0):
    current_user = request.user
    
    # if cart_count is less than 0, redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    
    if cart_count <= 0:
        return redirect('store:store')
    
    # if the cart count is not 0 then, we are going to collect the data submitted by the user in the 'Billing Address'
    
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        
        if form.is_valid():
            # store all the billing information inside the order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.city = form.cleaned_data['city']
            data.state = form.cleaned_data['state']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            
            
            # generate the orderID
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime(f"%d"))
            mt = int(datetime.date.today().strftime('%m'))
            
            d = datetime.date(yr, mt, dt)
            
            current_date = d.strftime(f"%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            
            
            # We are going to get an instance of the order class and get the order_number, is_ordered and the current user that submitted it
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total
            }
            
            
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('carts:checkout')
    
    
def payments(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    # print(body)
    # store the transaction detail into the payment method
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status']
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()
    
    # move the cart items to Order product table
    cart_items = CartItem.objects.filter(user=request.user)
    
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.ordered = True
        orderproduct.save()
        
        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        # the fact that the orderproduct has been saved, we use that id to actually assign it to the in order product table.
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(product_variation)
        orderproduct.save()
    # Reduce the quantity of the product
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()
    
    
    # then clear the cart.
    CartItem.objects.filter(user=request.user).delete()
    
    
    # send order recieve email to customer
    mail_subject = 'Thank you for your order!'
    context_string =  {
        'user':request.user,
        'order':order,
    }
    message = render_to_string('orders/order_recieved_email.html', context_string)
    to_email = request.user.email
    send_mail = EmailMessage(mail_subject, message, to=[to_email])
    send_mail.send()

    # send order number and transID back to sendData method in JSON format
    data = {
        'order_number':order.order_number,
        'transID':payment.payment_id
    }
    
    return JsonResponse(data)


def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
    
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products =  OrderProduct.objects.filter(order_id=order.id)

        
        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity
            
        
        payment = Payment.objects.get(payment_id=transID)
        context = {
            'subtotal': subtotal,
            'order': order,
            'order_products':ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment':payment,
        }
        return render(request, 'orders/order_complete.html', context)
    
    except(Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('/')
    