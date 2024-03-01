from django.db import models
from category.models import Category

# Create your models here.
class Product(models.Model):
    """this here is the product model which will have a foreign key with the category"""
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.IntegerField()
    image = models.ImageField(upload_to='product/', blank=True)
    stock = models.IntegerField()
    is_available = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)    
    modified_date = models.DateTimeField(auto_now=True)
    
    
    
    
    
    def __str__(self) -> str:
        return self.product_name