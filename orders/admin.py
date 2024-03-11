from django.contrib import admin

from .models import *

# Register your models here.
class OrderProductInLine(admin.TabularInline):
    model = OrderProduct
    extra = 0
    readonly_fields = ('payment', 'product',  'user', 'product_price', 'quantity', 'ordered',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'full_name', 'phone', 'email', 'city', 'state', 'order_total','status', 'is_ordered',)
    list_filter = ('status', 'is_ordered',)
    list_per_page = 20
    inlines = [OrderProductInLine]
    

admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
