from django.db import models
import uuid
from django.core.exceptions import ValidationError

class ShopCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, unique=True)
    thumbnail = models.ImageField(upload_to='Shop_Thumbnail/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Shop Categories'


class ProductCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Product Categories'


class Accompaniment(models.Model):  # Renamed to singular for clarity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Accompaniments'


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_category = models.ManyToManyField('ProductCategory', related_name='products',blank=True)  
    shop_category = models.ManyToManyField('ShopCategory', related_name='products', blank=True)
    possible_accompaniments = models.ManyToManyField('Accompaniment',blank=True, related_name='products')  # Fixed
    thumbnail = models.ImageField(upload_to='Image_Thumbnail/')
    is_pick_and_go = models.BooleanField(default=False)  
    delivery_time = models.PositiveIntegerField(null=True, blank=True, help_text="Time in minutes") 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    def clean(self):
        """Ensure delivery_time is required only if is_pick_and_go is False."""
        if not self.is_pick_and_go and self.delivery_time is None:
            raise ValidationError({'delivery_time': "Delivery time is required if the product is not 'Pick & Go'."})
    class Meta:
        verbose_name_plural = 'Products'
        ordering = ('name', 'created_at')
class FoodCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name=models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural='Food Categories'
        ordering=['name']
class Food(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name=models.CharField(max_length=255)
    price=models.DecimalField(max_digits=10, decimal_places=2)
    thumbnail=models.ImageField(upload_to='Food_Thumbnail/', null=True, blank=True)
    category=models.ForeignKey(FoodCategory, on_delete=models.CASCADE, related_name='foods_category')
    created_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    class Meta:
        verbose_name_plural='Foods'
        ordering=['name', 'created_at']   
