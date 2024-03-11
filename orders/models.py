from django.db import models



from accounts.models import *
from store.models import *
# Create your models here.
# for the order app, it needs 3 database table. the payment, order, order_product and 


class Payment(models.Model):
    """_summary_

    Args:
        models (_type_): _description_

    Returns:
        _type_: _description_
    """
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=255)
    payment_method = models.CharField(max_length=255)
    amount_paid = models.CharField(max_length=255) #this here is the total amount paid
    status = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self) -> str:
        return str(self.payment_id)
    
    
class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment =models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    order_note = models.CharField(max_length=255, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=25, choices=STATUS, default='New')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    
    def __str__(self) -> str:
        return str(self.first_name)
    
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def full_address(self):
        return f"{self.address_line_1} {self.address_line_2}"
    
class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self) -> str:
        return self.product.product_name
    
    
    
    
    