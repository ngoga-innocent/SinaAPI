from .models import Product,ProductCategory,ShopCategory,Accompaniment,Food,FoodCategory,Order
from rest_framework import serializers
from decimal import Decimal
from Payments.serilaizers import PaymentSerializer

class ShopCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopCategory
        fields = '__all__'
class AccompanimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Accompaniment
        fields = '__all__'
class ProductSerializer(serializers.ModelSerializer):
    product_category = serializers.PrimaryKeyRelatedField(
        many=True, queryset=ProductCategory.objects.all()
    )
    shop_category = serializers.PrimaryKeyRelatedField(
        many=True, queryset=ShopCategory.objects.all()
    )
    possible_accompaniments = possible_accompaniments = AccompanimentSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "product_category",
            "shop_category",
            "possible_accompaniments",
            "thumbnail",
            "is_pick_and_go",
            "delivery_time",
            "preparation_time",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate(self, attrs):
        """Ensure delivery_time is required if not pick & go."""
        # Use new values if provided, otherwise fall back to existing instance
        is_pick_and_go = attrs.get(
            "is_pick_and_go",
            getattr(self.instance, "is_pick_and_go", None)
        )
        delivery_time = attrs.get(
            "delivery_time",
            getattr(self.instance, "delivery_time", None)
        )

        if not is_pick_and_go and delivery_time is None:
            raise serializers.ValidationError(
                {"delivery_time": "Delivery time is required if the product is not 'Pick & Go serializer'."}
            )

        return attrs


# class ProductSerializer(serializers.ModelSerializer):
#     possible_accompaniments=AccompanimentSerializer(read_only=True,many=True)
#     # category=ProductCategorySerializer(read_only=True,many=True)
#     class Meta:
#         model = Product
#         fields = ['id','name','description','possible_accompaniments','price','thumbnail','is_pick_and_go','product_category','shop_category','delivery_time']
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
class OrderSerializer(serializers.ModelSerializer):
    order_payment_details=PaymentSerializer(source='order_payment',read_only=True)
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['id', 'user', 'total_price', 'created_at','order_payment_details']


# class ProductSerializer(serializers.ModelSerializer):
#     product_category = serializers.PrimaryKeyRelatedField(
#         many=True, queryset=ProductCategory.objects.all()
#     )
#     shop_category = serializers.PrimaryKeyRelatedField(
#         many=True, queryset=ShopCategory.objects.all()
#     )
#     possible_accompaniments = serializers.PrimaryKeyRelatedField(
#         many=True, queryset=Accompaniment.objects.all(), required=False
#     )

#     class Meta:
#         model = Product
#         fields = [
#             "id",
#             "name",
#             "description",
#             "price",
#             "product_category",
#             "shop_category",
#             "possible_accompaniments",
#             "thumbnail",
#             "is_pick_and_go",
#             "delivery_time",
#             "preparation_time",
#             "created_at",
#         ]
#         read_only_fields = ["id", "created_at"]

#     def validate(self, attrs):
#         """Ensure delivery_time is required if not pick & go."""
#         # Use new values if provided, otherwise fall back to existing instance
#         is_pick_and_go = attrs.get(
#             "is_pick_and_go",
#             getattr(self.instance, "is_pick_and_go", None)
#         )
#         delivery_time = attrs.get(
#             "delivery_time",
#             getattr(self.instance, "delivery_time", None)
#         )

#         if not is_pick_and_go and delivery_time is None:
#             raise serializers.ValidationError(
#                 {"delivery_time": "Delivery time is required if the product is not 'Pick & Go serializer'."}
#             )

#         return attrs



