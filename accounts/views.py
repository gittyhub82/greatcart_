from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required


from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


from .models import Account
from .forms import RegistrationForm
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
    return render(request, 'accounts/dashboard.html')

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        user = auth.authenticate(email=email, password=password)
        
        if user is not None:
            auth.login(request, user)
            messages.success(request, f"Welcome {user.first_name}! You are now logged in.")
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