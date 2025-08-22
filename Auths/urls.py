from django.urls import path
from .views import *

urlpatterns=[
    path('register',UserView.as_view()),
    path('login', LoginView.as_view()),
    path('logout',LogoutView.as_view(),name='logout'),
    path('profile', ProfileView.as_view(), name='profile_view'),
    path('reset-password', RequestPasswordResetView.as_view(), name='reset_password'),
    path('reset-password-confirm', PasswordResetConfirmView.as_view(), name='reset_password_confirm'),
    path('notification', NotificationListCreateView.as_view(), name='notification_list_create'),
    path('notification/<int:pk>/', NotificationDetailView.as_view(), name='notification_detail'),
    path('save_token/', save_push_token)
]