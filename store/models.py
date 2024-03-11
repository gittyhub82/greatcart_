from django.db import models
from django.urls import reverse
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
    
    def get_product_detail(self):
        return reverse('store:product_detail', args=[self.category.slug, self.slug])
    
    
    
    def __str__(self) -> str:
        return self.product_name
    

# time to deal with the product variation

variation_category_choice = (
    ('color', 'color'),
    ('size', 'size'),
)

class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(variation_category='color', is_active=True)
    
    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)

class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category = models.CharField(max_length=255, choices=variation_category_choice)
    variation_value = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)
    
    objects = VariationManager()
    
    def __str__(self) -> str:
        return str(self.variation_value)