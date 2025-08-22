from .models import Payment
from rest_framework import serializers
from Auths.serializers import UserSerializer
class PaymentSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)

    class Meta:
        fields = [
            'id',
            'ref',
            'customer',
            'phone_number',
            'amount',
            'status',
            'is_scanned',
            'qr_code',
            # 'qr_code_url',
            'created_at',
        ]
        
        model=Payment
