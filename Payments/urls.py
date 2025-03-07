from django.urls import path
from .views import PaymentView,WebHook,checkPayment,ConfirmQrScan
urlpatterns =[
    path('', PaymentView.as_view()),
    path('paymentCheck/<uuid:payment_id>',checkPayment),
    path('webhook',WebHook),
    path('qrscan/',ConfirmQrScan.as_view())
]