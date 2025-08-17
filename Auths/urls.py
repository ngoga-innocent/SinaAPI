from django.urls import path
from .views import *

urlpatterns=[
    path('register',UserView.as_view()),
    path('login', LoginView.as_view()),
    path('logout',LogoutView.as_view(),name='logout'),
    path('profile', ProfileView.as_view(), name='profile_view'),
    path('reset-password', RequestPasswordResetView.as_view(), name='profile_view'),
    path('reset-password-confirm', PasswordResetConfirmView.as_view(), name='profile_view'),
]