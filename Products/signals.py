from django.db.models.signals import post_save,m2m_changed
from django.dispatch import receiver
from .models import Order,Product

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
    Restore stock when an order is cancelled or rejected.
    """
    if not created:
        # Check if the order status changed to cancelled or rejected
        if instance.payment_status in ["cancelled", "rejected"]:
            # Loop through all OrderItems
            for item in instance.products.all():
                product = item.product
                product.stock += item.quantity  # Restore stock
                product.save()
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

