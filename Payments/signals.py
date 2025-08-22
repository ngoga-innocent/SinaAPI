from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment
from Auths.models import User,Notification
from Products.models import Order
from .views import PaymentView  # Import the updated view
from django.db import transaction
@receiver(post_save, sender=Payment)
def generate_qr_on_payment_save(sender, instance, created, **kwargs):
    if not instance.qr_code:  
        print(f"DEBUG: Generating QR code for payment {instance.id} with status {instance.customer}")
        if instance.customer_id:
            customer = User.objects.get(id=instance.customer_id)
            print(f"DEBUG: Found customer {customer.full_name} for payment {instance.id}")
        transaction.on_commit(lambda: PaymentView.generate_QrCode(
            instance.customer_id,
            customer.full_name,
            customer.phone_number,
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
        old_status = order.payment_status
        order.payment_status = instance.status  # Sync order status with payment status
        order.save()
        
        print(f"DEBUG: Order {order.id} status updated to {order.payment_status}, order is now ")
        if old_status != instance.status:
            # Create notification for the user
            if order.user:  # Make sure user exists
                Notification.objects.create(
                    title="Order Payment Status Updated",
                    message=f"Your order #{order.id} payment status changed to {instance.status}.",
                    notification_type="user",
                    user=order.user
                )
                print(f"DEBUG: Notification sent to user {order.user.id} for order {order.id}")

    

    except Order.DoesNotExist:
        print(f"WARNING: No order found for payment {instance.id}")
        pass

