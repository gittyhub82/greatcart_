from django.contrib import admin

# Register your models here.
from .models import *


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'slug': ('category_name',)
    }
    
admin.site.register(Category, CategoryAdmin)