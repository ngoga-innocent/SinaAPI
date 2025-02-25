from django.urls import path
from .views import ProductView,ProductCategoryView,ShopCategoryView,FoodCategoryView
urlpatterns =[
    path('',ProductView.as_view()),
    path('category/',ProductCategoryView.as_view()),
    path('category/<uuid:category_id>',ProductCategoryView.as_view()),
    path('shopcategory/',ShopCategoryView.as_view()),
    path('foodcategory/',FoodCategoryView.as_view()),
]