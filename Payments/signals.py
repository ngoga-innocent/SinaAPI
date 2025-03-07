from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment
from Products.models import Order
from .views import PaymentView  # Import the updated view
from django.db import transaction
@receiver(post_save, sender=Payment)
def generate_qr_on_payment_save(sender, instance, created, **kwargs):
    if not created and not instance.qr_code:  
        transaction.on_commit(lambda: PaymentView.generate_QrCode(
            instance.customer_id,
            instance.amount,
            instance.ref,
            instance.id,
            instance.status
        ))


@receiver(post_save, sender=Payment)
def update_order_payment_status(sender, instance, **kwargs):
    """
    Update the order's payment_status when the payment status changes.
    """
    try:
        # Find the order associated with this payment
        order = Order.objects.get(order_payment=instance)
        print(order.id,instance.status)
        # Update order payment status
        order.payment_status = instance.status  # Sync order status with payment status
        order.save()
        
        print(f"DEBUG: Order {order.id} status updated to {order.payment_status}, order is now ")

    except Order.DoesNotExist:
        print(f"WARNING: No order found for payment {instance.id}")
        pass
