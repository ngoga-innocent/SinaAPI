from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import Product, ProductCategory,ShopCategory,FoodCategory, Food
from .serializers import ProductSerializer,ProductCategorySerializer,ShopCategorySerializer,FoodCategorySerializer

class ProductView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get("search", "")
        product_id = request.query_params.get("product_id", None)  # For fetching similar products

        if product_id:
            # Get the product and its categories
            try:
                product = Product.objects.get(id=product_id)
                categories = product.product_category.all()  # Get related categories
                # Fetch other products in the same categories (excluding itself)
                similar_products = Product.objects.filter(product_category__in=categories).exclude(id=product.id).distinct()
                serializer = ProductSerializer(similar_products, many=True)
                return Response({"data": serializer.data}, status=200)
            except Product.DoesNotExist:
                return Response({"error": "Product not found"}, status=404)

        # Searching products by name
        if query:
            products = Product.objects.filter(Q(name__icontains=query))
        else:
            products = Product.objects.all()

        serializer = ProductSerializer(products, many=True,context={"request": request})
        return Response({"data": serializer.data}, status=200)
class ProductCategoryView(APIView):
    def get(self, request,category_id=None, *args, **kwargs):
        if category_id is not None:
            try:
                category = ProductCategory.objects.get(id=category_id)
                products = category.products.all()
                serializer = ProductSerializer(products, many=True,context={"request": request})
                return Response({"data": serializer.data}, status=200)
            except ProductCategory.DoesNotExist:
                return Response({"error": "Product category not found"}, status=404)
        categories = ProductCategory.objects.all()
        serializer = ProductCategorySerializer(categories, many=True,context={"request": request})
        return Response({"data": serializer.data}, status=200)
class ShopCategoryView(APIView):
    def get(self, request, *args, **kwargs):
        categories = ShopCategory.objects.all()
        serializer = ShopCategorySerializer(categories, many=True,context={"request": request})
        return Response({"data": serializer.data}, status=200)
class FoodCategoryView(APIView):
    def get(self, request, *args, **kwargs):
        food_categories = FoodCategory.objects.all()
        serializer=FoodCategorySerializer(food_categories, many=True, context={"request": request})
        return Response({"data": serializer.data}, status=200)
        