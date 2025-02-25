from django.urls import path
from .views import PaymentView,WebHook,checkPayment
urlpatterns =[
    path('', PaymentView.as_view()),
    path('paymentCheck/<uuid:payment_id>',checkPayment),
    path('webhook',WebHook)
]