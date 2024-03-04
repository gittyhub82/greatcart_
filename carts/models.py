from django.db import models
from store.models import Product, Variation
from accounts.models import Account
# Create your models here.


# Remember, the cart is created so as to save the session ID of the current user


class Cart(models.Model):
    cart_id = models.CharField(max_length=255, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self) -> str:
        return self.cart_id
    
    
# so here is for the cart item = cart + product
class CartItem(models.Model):
    # the reason why this is done is when a user isn't logged in and they have add someething to their cart. Next, when they are about to checkout, they need to log in
    # when they login, then the cartitems that the unlogged user adds to their cart, is not transferred to the log in user
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    # then it needs to show how many product are in the cartitem
    quantity = models.IntegerField()
    variations = models.ManyToManyField(Variation, blank=True)
    is_active = models.BooleanField(default=True)
    
    # this here is for each of the instance of the cartitem, which calculates the total of each product
    def sub_total(self):
        return (self.product.price * self.quantity)
    
    
    def __str__(self) -> str:
        return str(self.product)
