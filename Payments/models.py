from django.db import models
import uuid
from Auths.models import User
# from Products.models import Product
# Create your models here.
class Payment(models.Model):
    STATUS_CHOICE=(
        ('pending','Pending'),
        ('completed','completed'),
        ('failed','Failed'),
    )
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    ref=models.CharField(max_length=255)
    customer=models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number=models.CharField(max_length=15)
    amount=models.DecimalField(max_digits=10, decimal_places=2)
    status=models.CharField(max_length=10,choices=STATUS_CHOICE)
    qr_code = models.ImageField(upload_to='qrcodes/', null=True, blank=True)
    is_scanned=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural='Payments'
        ordering=['-created_at']
# class Order(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
#     payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='orders_payment')
#     products = models.ManyToManyField(Product, through="OrderItem")  # Through model for quantity
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2)
#     status = models.CharField(
#         max_length=20, choices=[
#             ('pending', 'Pending'),
#             ('completed', 'Completed'),
#             ('cancelled', 'Cancelled'),
#         ],
#         default='pending'
#     )
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Order {self.id} - {self.user.username}"

# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.PositiveIntegerField(default=1)  # Stores number of items

#     def __str__(self):
#         return f"{self.product.name} (x{self.quantity}) in Order {self.order.id}"
    