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
from rest_framework import generics
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.decorators import api_view
from .serilaizers import PaymentSerializer
from rest_framework.permissions import IsAuthenticated,IsAdminUser
import logging
logger = logging.getLogger(__name__)
load_dotenv()
# UPDATING PAYMENT and Retrieving Payment Status

class PaymentListView(generics.ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminUser]
class PaymentRetrieveUpdate(generics.RetrieveUpdateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminUser]

    def patch(self, request, *args, **kwargs):
        try:
            print("Request data:", request.data)
            return super().patch(request, *args, **kwargs)
        except Exception as e:
            print("Error occurred:", e)
            return Response(
                {"error": "Failed to update payment"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
class PaymentView(APIView):
    permission_classes = [IsAuthenticated]  # Require authentication

    BASE_URL = "https://payments.paypack.rw/api"
    @staticmethod
    def authenticate_paypack():
        url = f"{PaymentView.BASE_URL}/auth/agents/authorize"
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
        # print(request.user)
        # print(phone_number,amount)
        
        return self.deposit(request.user,phone_number,amount)
        # Authenticate with Paypack API
    @staticmethod    
    def deposit(user,phone_number,amount):
        if not phone_number or not amount:
            return Response({"error": "Phone number and amount are required"}, status=status.HTTP_400_BAD_REQUEST)
        access_token = PaymentView.authenticate_paypack()
        # print(access_token)
        if not access_token:
            return Response({"error": "Failed to authenticate payment service"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Process payment request
        url = f"{PaymentView.BASE_URL}/transactions/cashin"
        payload = json.dumps({"amount": amount, "number": phone_number})
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}",
            "X-Webhook-Mode":"production"
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
            customer=user,  # Authenticated user
            phone_number=phone_number,
            amount=amount,
            status=payment_status
        )
        # if payment:
        #     self.generate_QrCode(request.user.id,amount,payment.id,payment.id,payment_status)
        
        return Response({"message": "Payment recorded successfully", "payment_id": payment.id, "status": payment.status}, status=status.HTTP_200_OK)
    @staticmethod
    def generate_QrCode(customer_id,customer_name,customer_phone, amount, transaction_ref, payment_id, payment_status):
        """Generate a QR code and attach it to the payment record."""
        print("generating QRCODE")
        try:
            # Try to retrieve payment and log
            payment = Payment.objects.get(id=payment_id)
            print(f"Payment found: ID={payment.id}, Status={payment.status}, Amount={payment.amount}")
            
            if payment.qr_code:
                print(f"QR code already exists for Payment ID={payment.id}")
                return Response({"message": "QR Code already exists"}, status=200)

            # Create the payment data dictionary
            payment_data = {
                'customer_id': customer_id,
                'payment_id': str(payment_id),
                'customer_name': str(customer_name),
                'customer_phone': str(customer_phone),
                'amount': str(amount),  # Convert Decimal to string
                'status': payment_status,
                'transaction_id': transaction_ref,
                'timestamp': timezone.now().isoformat(),
            }

            logger.info(f"Payment data for QR code: {payment_data}")

            # Convert the dictionary to a valid JSON string
            payment_data_str = json.dumps(payment_data)
            logger.info(f"JSON data for QR: {payment_data_str}")

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

            # Save QR code to the payment object
            payment.qr_code.save(f"{transaction_ref}_qrcode.png", qr_code_file)
            payment.save(update_fields=['qr_code'])
            print(payment_data)
            logger.info(f"QR code successfully generated and saved for Payment ID={payment.id}")
            return Response({'qr_code': "QR Code generated and saved in database"}, status=200)

        except Payment.DoesNotExist:
            logger.error(f"Payment with ID {payment_id} not found.")
            return Response({"error": "Payment not found"}, status=404)

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {str(e)}")
            return Response({"error": "Error in JSON data"}, status=500)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response({"error": "Internal server error"}, status=500)
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
   

class ConfirmQrScan(APIView):
    def post(self,request):
        payment_id=request.data.get('payment_id')
        
        try:
            payment=Payment.objects.get(id=payment_id)
            if payment.is_scanned:
                return Response({"message":"Payment Already Scanned","valid":False,"data":PaymentSerializer(payment).data},status=200)
            payment.is_scanned=True
            payment_save=payment.save()
            
            return Response({"message":"Qr Code Scanned Correctly","valid":True,"data":PaymentSerializer(payment_save).data},status=201)
        except Payment.DoesNotExist:
            return Response({"message":"Invalid Payment","valid":False},status=400)