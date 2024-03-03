from django.db import models
from store.models import Product, Variation
# Create your models here.


# Remember, the cart is created so as to save the session ID of the current user


class Cart(models.Model):
    cart_id = models.CharField(max_length=255, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self) -> str:
        return self.cart_id
    
    
# so here is for the cart item = cart + product
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    # then it needs to show how many product are in the cartitem
    quantity = models.IntegerField()
    variations = models.ManyToManyField(Variation, blank=True)
    is_active = models.BooleanField(default=True)
    
    # this here is for each of the instance of the cartitem, which calculates the total of each product
    def sub_total(self):
        return (self.product.price * self.quantity)
    
    
    def __str__(self) -> str:
        return str(self.product)
