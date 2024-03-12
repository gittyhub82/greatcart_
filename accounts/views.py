from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
import requests


from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


from .models import Account
from .forms import *
from carts.models import *
from carts.views import _cart_id

from orders.models import Order, OrderProduct
# Create your views here.


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # create variaables based on the forms submitted and store them
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            username = email.split("@")[0]
            
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
            user.phone_number = phone_number
            user.save()
            
            # USER ACTIVATION
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account.'
            context_string =  {
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            }
            message = render_to_string('accounts/account_verification_email.html', context_string)
            to_email = email
            send_mail = EmailMessage(mail_subject, message, to=[to_email])
            send_mail.send()
            # messages.success(request, f'Thank you for registering with us. We have sent you a verification link to {email}.')
            return redirect('/accounts/login/?command=verification&email='+email)
            
    else:
        form = RegistrationForm()
    
    context = {
        'form' : form,
    }
    return render(request, 'accounts/register.html',context)


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account has been activated')
        return redirect('accounts:login')
    
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('accounts:register')

@login_required
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    userprofile = UserProfile.objects.get(user_id=request.user.id)
    order_count = orders.count()
    
    context = {
        'order_count':order_count,
        'userprofile':userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        user = auth.authenticate(email=email, password=password)
        
        if user is not None:
            # check if there is any cart item before user logs in
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                
                
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    
                    product_variation = []
                    
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))
                        
                    
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    
                    # loop through the cart_item and store it values in the existing variation list
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                        
                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        
                        else:
                            # what this does is if the cart item is not in logged in user cart item, then as the user logged in, assign it to them
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
                        
                    # # assiging the cart item to the logged in user
                    # for item in cart_item:
                    #     item.user = user
                    #     item.save()
                
            except:
                pass
            auth.login(request, user)
            messages.success(request, f"Welcome {user.first_name}! You are now logged in.")
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    next_page = params['next']
                    return redirect(next_page)
                
            except:
                return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('accounts:login')
    
    return render(request, 'accounts/login.html')


@login_required
def logout(request):
    auth.logout(request)
    messages.success(request, 'You have logged out.')
    return redirect('accounts:login')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        
        if Account.objects.filter(email=email).exists():
            # this here is making sure the user enters the 
            user = Account.objects.get(email__exact=email)
            
            # RESET PASSWORD EMAIL
            current_site = get_current_site(request)
            mail_subject = 'Please reset your password.'
            context_string =  {
                'user':user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            }
            message = render_to_string('accounts/reset_password_email.html', context_string)
            to_email = email
            send_mail = EmailMessage(mail_subject, message, to=[to_email])
            send_mail.send()
            messages.success(request, 'password reset email has been sent to your email address')
            return redirect('accounts:login')
        else:
            
            messages.error(request, 'Account does not exist.')
            return redirect('accounts:forgot_password')
        
    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Reset Your Password')
        return redirect('accounts:reset_password')
    
    else:
        messages.error(request, 'This link has expired')
        return redirect('accounts:forgot_password')
    

 
def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'The password reset was successful.')
            return redirect('accounts:login')
            
        else:
            messages.error(request, 'Password did not match')
            return redirect('accounts:reset_password')
    return render(request, 'accounts/reset_password.html')

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders':orders
    }
    return render(request, 'accounts/my_orders.html', context)


@login_required
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('accounts:edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user_form':user_form,
        'profile_form':profile_form,
        'userprofile':userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        
        user = Account.objects.get(username__exact=request.user.username)
        
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                # logging the user out the moment they change their password
                # auth.logout(user)
                messages.success(request, 'Password Updated Successfully.')
                return redirect('account:change_password')
            else:
                messages.error(request, 'PLEASE ENTER VALID CURRENT PASSWORD!')
                return redirect('accounts:change_password')
        else:
            messages.error(request, 'Password Does Not Match!')
            return redirect('accounts:change_password')
    return render(request, 'accounts/change_password.html')

@login_required
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    
    subtotal = 0
    
    for i in order_detail:
        subtotal += i.product_price + i.quantity
    context = {
        'order_detail':order_detail,
        'order':order,
        'subtotal':subtotal
    }
    return render(request, 'accounts/order_detail.html', context)