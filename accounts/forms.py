from typing import Any
from django import forms


from .models import *


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter Your Password',
        'class': 'form-control'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Confirm Your Password',
        'class': 'form-control',
    }))
    class Meta:
        model = Account
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone_number', 
            'password',
        ]
        
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Type Your First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Type Your Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Type Your Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Type Your Email'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            
    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        
        if password != confirm_password:
            raise forms.ValidationError('Password does not match!')