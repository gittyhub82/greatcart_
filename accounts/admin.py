from django.contrib import admin
# to make your password read-only you need to import 

from django.contrib.auth.admin import UserAdmin


from .models import *

# Register your models here.
class AccountAdmin(UserAdmin):
    list_display = (
        'email',
        'first_name',
        'last_name',
        'username',
        'last_login',
        'is_active',
    )
    readonly_fields = (
        'last_login',
        'is_active',
    )
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

admin.site.register(Account, AccountAdmin)
