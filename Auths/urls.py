from django.urls import path
from .views import *

urlpatterns=[
    path('register',UserView.as_view()),
    path('login', LoginView.as_view()),
    path('profile', ProfileView.as_view(), name='profile_view'),
]