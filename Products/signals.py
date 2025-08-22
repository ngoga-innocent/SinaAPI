from django.db.models.signals import post_save,m2m_changed
from django.dispatch import receiver

from Auths.push_Notification import send_push_notification
from .models import Order,Product
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

# @receiver(m2m_changed, sender=Order.products.through)
# def reduce_stock_on_order(sender, instance, action, pk_set, **kwargs):
#     """
#     Reduce product stock when products are added to an order.
#     Assumes quantity = 1 per product in the order.
#     """
#     if action == "post_add":
#         for product_id in pk_set:
#             product = Product.objects.get(pk=product_id)
#             if product.stock > 0:
#                 product.stock -= 1
#                 product.save(update_fields=["stock"])
#             else:
#                 # Not enough stock, cancel order
#                 instance.order_status = "cancelled"
#                 instance.save(update_fields=["order_status"])

