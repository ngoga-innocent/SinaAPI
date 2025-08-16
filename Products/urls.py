from django.urls import path
from .views import ProductView,ProductCategoryView,ShopCategoryView,FoodCategoryView,OrderDetailView,OrderCreateAPIView,ProductListCreateView
urlpatterns =[
    path('',ProductListCreateView.as_view()),
    path('category/',ProductCategoryView.as_view()),
    path('category/<uuid:category_id>',ProductCategoryView.as_view()),
    path('shopcategory/',ShopCategoryView.as_view()),
    path('foodcategory/',FoodCategoryView.as_view()),
    path('orders/', OrderCreateAPIView.as_view(), name='order-list-create'),
    path('orders/<uuid:pk>/', OrderDetailView.as_view(), name='order-detail'),

]