from django.db import models
import uuid
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from Payments.models import Payment
User = get_user_model()

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


class Accompaniment(models.Model):  
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    preparation_time = models.PositiveIntegerField(default=0)  # In minutes

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Accompaniments'

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    product_category = models.ManyToManyField('ProductCategory', related_name='products', blank=True)  
    shop_category = models.ManyToManyField('ShopCategory', related_name='products', blank=True)
    possible_accompaniments = models.ManyToManyField('Accompaniment', blank=True, related_name='products')  
    thumbnail = models.ImageField(upload_to='Image_Thumbnail/')
    is_pick_and_go = models.BooleanField(default=False)  
    delivery_time = models.PositiveIntegerField(null=True, blank=True, help_text="Time in minutes") 
    preparation_time = models.PositiveIntegerField(default=0)  # In minutes
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def clean(self):
        # Only check if delivery_time is None and is_pick_and_go is False
        # but allow existing value if instance exists
        if not self.is_pick_and_go:
            if self.pk:  # updating existing instance
                existing = Product.objects.get(pk=self.pk)
                if self.delivery_time is None and existing.delivery_time is None:
                    raise ValidationError({
                        'delivery_time': "Delivery time is required if the product model is not 'Pick & Go'."
                    })
            else:  # creating new instance
                if self.delivery_time is None:
                    raise ValidationError({
                        'delivery_time': "Delivery time is required if the product model is not 'Pick & Go'."
                    })


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
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    thumbnail = models.ImageField(upload_to='Food_Thumbnail/', null=True, blank=True)
    category = models.ForeignKey(FoodCategory, on_delete=models.CASCADE, related_name='foods_category')
    preparation_time = models.PositiveIntegerField(default=0)  # In minutes
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Foods'
        ordering = ['name', 'created_at']
class Order(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'completed'),
        ('failed', 'failed'),
    ]
    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid','Paid'),
        ('accepted', 'In Progress'),
        ('ready', 'Completed'),
        ('delivered', 'Delivered'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_orders")
    # products = models.ManyToManyField('Product', blank=True, related_name="product_orders")
    # products = models.ManyToManyField("Product", through="OrderItem", blank=True)
    foods = models.ManyToManyField('Food', blank=True, related_name="food_orders")
    accompaniments = models.ManyToManyField('Accompaniment', blank=True, related_name="orders")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    order_payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
    order_status=models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    preparation_time = models.PositiveIntegerField(default=0)  # In minutes
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.phone_number} - {self.payment_status}"
class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey("Order", related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="order_items", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def clean(self):
        print(f"DEBUG: Validating stock for {self.product.name}, requested {self.quantity}, available {self.product.stock}")
        if self.product.stock < self.quantity:
            raise ValidationError(f"Not enough stock for {self.product.name}")

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        self.clean()
        super().save(*args, **kwargs)
        # Reduce stock only when creating
        if is_new:
            self.product.stock -= self.quantity
            self.product.save(update_fields=["stock"])

    def __str__(self):
        return f"{self.quantity} x {self.product.name} for order {self.order.id}"