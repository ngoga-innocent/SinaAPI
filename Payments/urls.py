from django.urls import path
from .views import PaymentView,WebHook,checkPayment,ConfirmQrScan,PaymentListView,PaymentRetrieveUpdate
urlpatterns =[
    path('', PaymentView.as_view()),
    path('payment/<uuid:pk>/', PaymentRetrieveUpdate.as_view()),
    path('all-payments/', PaymentListView.as_view()),
    
    path('paymentCheck/<uuid:payment_id>',checkPayment),
    path('webhook',WebHook),
    path('qrscan/',ConfirmQrScan.as_view())
]