from django.contrib import admin
# to make your password read-only you need to import 

from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

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

class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self, object):
        return format_html('<img src="{}" width="30" style="border-radius:50%;">'.format(object.profile_picture.url))
    thumbnail.short_description = 'Profile Picture'
    list_display = ('thumbnail','user', 'city', 'state',)

admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
