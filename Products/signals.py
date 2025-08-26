from django.db.models.signals import post_save,m2m_changed
from django.dispatch import receiver
from django.db.models.signals import pre_save
from Auths.push_Notification import send_push_notification
from Products.calculate_distance_time import calculate_distance_and_time
from .models import Order,Product,InventoryUpdateHistory
from Auths.models import Notification
@receiver(post_save, sender=Order)
def auto_cancel_order_on_payment_failure(sender, instance, **kwargs):
    """
    Cancel the order automatically if payment fails.
    """
    if instance.payment_status == "failed" and instance.order_status not in ["cancelled", "rejected"]:
        instance.order_status = "cancelled"
        instance.save(update_fields=["order_status"])
    elif instance.payment_status == "completed" and instance.order_status == "pending":
        instance.order_status = "paid"
        instance.save(update_fields=["order_status"])

@receiver(post_save, sender=Order)
def handle_order_status_change(sender, instance, created, **kwargs):
    """
    Handle order creation and updates:
    - Notify user on creation
    - Restore stock if order is cancelled/rejected
    - Notify user on status/payment updates
    """
    if created:
        # New order created
        if instance.user:
            Notification.objects.create(
                title="Order Created",
                message=f"Your order #{instance.id} has been created successfully.",
                notification_type="user",
                user=instance.user
            )
    else:
        # Order was updated
        if instance.payment_status in ["cancelled", "rejected"]:
            # Restore stock for all products in the order
            for item in instance.products.all():
                product = item.product
                product.stock += item.quantity
                product.save()

        # Always notify the user on update
        if instance.user:
            Notification.objects.create(
                title="Order Updated",
                message=(
                    f"Your order #{instance.id} status is now '{instance.order_status}' "
                    f"and payment status is '{instance.payment_status}'."
                ),
                notification_type="user",
                user=instance.user
            )
            if instance.user.device_token:
                send_push_notification(
                    instance.user.device_token.expo_push_token,
                    "Order Updated",
                    f"Order #{instance.id} is now {instance.order_status}, payment: {instance.payment_status}"
            )
@receiver(post_save, sender=InventoryUpdateHistory)
def create_inventory_update_notification(sender, instance, created, **kwargs):
    """
    Create a notification when inventory is updated.
    """
    if created:
        instance.product.stock += instance.quantity
        instance.product.save(update_fields=["stock"])
        Notification.objects.create(
            title="Inventory Updated",
            message=(
                f"Inventory for {instance.product.name} has been updated: {instance.quantity:+}."
            ),
            notification_type="admin",
        )
        # Optionally update the product stock
        
@receiver(pre_save, sender=Order)
def set_distance_and_time(sender, instance, **kwargs):
    if instance.latitude and instance.longitude:
        distance, time = calculate_distance_and_time(instance.latitude, instance.longitude)
        instance.distance_km = distance
        instance.estimated_time_min = time