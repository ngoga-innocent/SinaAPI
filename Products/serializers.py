from .models import Product,ProductCategory,ShopCategory,Accompaniment,Food,FoodCategory
from rest_framework import serializers



class ShopCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopCategory
        fields = '__all__'
class AccompanimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accompaniment
        fields = '__all__'
class ProductSerializer(serializers.ModelSerializer):
    possible_accompaniments=AccompanimentSerializer(read_only=True,many=True)
    # category=ProductCategorySerializer(read_only=True,many=True)
    class Meta:
        model = Product
        fields = ['id','name','description','possible_accompaniments','price','thumbnail','is_pick_and_go','delivery_time']
class ProductCategorySerializer(serializers.ModelSerializer):
    products=ProductSerializer(read_only=True,many=True)
    class Meta:
        model = ProductCategory
        fields = ['id','name','products']
class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = '__all__'
class FoodCategorySerializer(serializers.ModelSerializer):
    foods=FoodSerializer(read_only=True,many=True,source='foods_category')
    class Meta:
        model = FoodCategory
        fields = ['id','name','foods']