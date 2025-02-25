from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment
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
