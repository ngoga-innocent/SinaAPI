from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from .models import Payment
import requests
import json
import uuid
import os
from dotenv import load_dotenv
import qrcode
from io import BytesIO
from django.utils import timezone
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.decorators import api_view
from .serilaizers import PaymentSerializer
load_dotenv()
class PaymentView(APIView):
    permission_classes = [IsAuthenticated]  # Require authentication

    BASE_URL = "https://payments.paypack.rw/api"

    def authenticate_paypack(self):
        url = f"{self.BASE_URL}/auth/agents/authorize"
        payload = json.dumps({
            "client_id": os.getenv("PAYPACK_CLIENT_ID"),
            "client_secret": os.getenv("PAYPACK_CLIENT_SECRET")
        })
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        
        response = requests.post(url, headers=headers, data=payload)
        # print(response)
        if response.status_code == 200:
            return response.json().get("access")
        return None

    def post(self, request):
        phone_number = request.data.get("phone_number")
        amount = request.data.get("amount")
        print(request.user)
        print(phone_number,amount)
        if not phone_number or not amount:
            return Response({"error": "Phone number and amount are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate with Paypack API
        access_token = self.authenticate_paypack()
        # print(access_token)
        if not access_token:
            return Response({"error": "Failed to authenticate payment service"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Process payment request
        url = f"{self.BASE_URL}/transactions/cashin"
        payload = json.dumps({"amount": amount, "number": phone_number})
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
            "X-Webhook-Mode":"development"
        }
        
        response = requests.post(url, headers=headers, data=payload)
        response_data = response.json()
        ref=response_data.get('ref')
        # print(response_data)
        # Determine payment status
        payment_status = "pending"  # Default to pending
        if response.status_code == 400:
            payment_status = "failed"
            
        
        # print(request.user)
        # Save payment record in the database
        payment = Payment.objects.create(
            ref=ref,
            customer=request.user,  # Authenticated user
            phone_number=phone_number,
            amount=amount,
            status=payment_status
        )
        # if payment:
        #     self.generate_QrCode(request.user.id,amount,payment.id,payment.id,payment_status)
        
        return Response({"message": "Payment recorded successfully", "payment_id": payment.id, "status": payment.status}, status=status.HTTP_200_OK)
    @staticmethod
    def generate_QrCode(customer_id, amount, transaction_ref, payment_id, payment_status):
        """Generate a QR code and attach it to the payment record."""
        
        # Prevent unnecessary processing if QR code already exists
        try:
            payment = Payment.objects.get(id=payment_id)
            if payment.qr_code:  
                return Response({"message": "QR Code already exists"}, status=200)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=404)

        # Create the payment data string
        payment_data = {
            'customer_id': customer_id,
            'amount': amount,
            'status': payment_status,
            'transaction_id': transaction_ref,
            'timestamp': timezone.now().isoformat(),
        }
        payment_data_str = str(payment_data)

        # Generate the QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(payment_data_str)
        qr.make(fit=True)
        
        # Convert QR Code to an image file
        img = qr.make_image(fill='black', back_color='white')
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)

        # Convert to a Django file object
        qr_code_file = ContentFile(img_io.getvalue(), name=f"{transaction_ref}_qrcode.png")

        # ✅ Correct way: Use `.save(update_fields=['qr_code'])`
        payment.qr_code.save(f"{transaction_ref}_qrcode.png", qr_code_file)
        payment.save(update_fields=['qr_code'])  # Avoid triggering `post_save` signal

        return Response({'qr_code': "QR Code generated and saved in database"}, status=200)
@csrf_exempt
@api_view(["POST", "HEAD"])
def WebHook(request):
    if request.method == "HEAD":
        return JsonResponse({"message": "Webhook endpoint available"}, status=200)
    
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))
            print("Webhook data:", data)

            # Ensure we correctly extract `ref` from the nested "data" field
            transaction_data = data.get('data', {})
            ref = transaction_data.get('ref')
            status = 'completed' if transaction_data.get('status')=='successful' else transaction_data.get('status')
            phone_number = transaction_data.get('client')
            amount = transaction_data.get('amount')

            if not ref:
                return JsonResponse({"error": "Missing reference in webhook payload"}, status=400)

            try:
                payment = Payment.objects.get(ref=ref)
                payment.status = status
                payment.save()
                print("Updated payment:", payment)
            except Payment.DoesNotExist:
                print("Payment not found:", ref)
            
            return JsonResponse({"message": "Webhook received"}, status=200)
        
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)
@api_view(["GET", "HEAD"])
def checkPayment(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
        serializer=PaymentSerializer(payment,context={'request': request})
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)
    except Payment.DoesNotExist:
        return Response({"data": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
   

