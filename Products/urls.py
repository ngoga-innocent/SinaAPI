from django.urls import path
from .views import ListOrderView,ProductCategoryView,ProductReadUpdateView,ShopCategoryListCreateView,FoodCategoryListCreateView,FoodCategoryDetailView,OrderDetailView,OrderCreateAPIView,ProductListCreateView
urlpatterns =[
    path('',ProductListCreateView.as_view()),
    path('<uuid:pk>',ProductReadUpdateView.as_view()),
    path('category/',ProductCategoryView.as_view()),
    path('category/<uuid:category_id>',ProductCategoryView.as_view()),
    path('shopcategory/',ShopCategoryListCreateView.as_view()),
    path('foodcategory/',FoodCategoryListCreateView.as_view()),
    path('foodcategory/<uuid:pk>',FoodCategoryDetailView.as_view()),
    path('orders/', OrderCreateAPIView.as_view(), name='order-list-create'),
    path('all-orders/',ListOrderView.as_view()),
    path('orders/<uuid:pk>/', OrderDetailView.as_view(), name='order-detail'),

]