from urllib import request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from rest_framework import generics, permissions,status,serializers
from decimal import Decimal
from .models import Product, ProductCategory,ShopCategory,FoodCategory, Food,Order,Accompaniment,OrderItem
from .serializers import ProductSerializer,ProductCategorySerializer,ShopCategorySerializer,FoodCategorySerializer,OrderSerializer
from Auths.models import User
from Payments.views import PaymentView
from Payments.models import Payment
from django.db.models import Max
from rest_framework.decorators import api_view
from .filters import ProductFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAdminUser
from django.core.exceptions import ValidationError
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
class ProductListCreateView(generics.ListCreateAPIView):
    # print(request.data)
    queryset = Product.objects.all().order_by("-created_at")
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly] 
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = ProductFilter
    ordering_fields = ["price", "created_at", "preparation_time"]
    search_fields = ["name", "description"]
    
class ProductReadUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset=Product.objects.all()
    serializer_class=ProductSerializer
    permission_classes=[IsAuthenticatedOrReadOnly]
class ShopCategoryListCreateView(generics.ListCreateAPIView):
    queryset = ShopCategory.objects.all().order_by("-created_at")
    serializer_class = ShopCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ShopCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShopCategory.objects.all()
    serializer_class = ShopCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

@api_view(['GET'])
def shop_products(request, shop_id):
    """
    Return all products belonging to a specific shop.
    """
    try:
        products = Product.objects.filter(shop_category=shop_id)  # simpler lookup
        if not products.exists():
            return Response(
                {"error": "No products found for this shop"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except ValidationError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        # Catch any unexpected errors
        print("Unexpected error:", str(e))
        return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- FoodCategory CRUD ---
class FoodCategoryListCreateView(generics.ListCreateAPIView):
    queryset = FoodCategory.objects.all().order_by("name")
    serializer_class = FoodCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class FoodCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FoodCategory.objects.all()
    serializer_class = FoodCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
class OrderCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self,request):
        orders=Order.objects.filter(user=request.user)
        serializer=OrderSerializer(orders,many=True,context={"request": request})
        return Response({"data": serializer.data}, status=200)
    def post(self, request):
        try:
            print("DEBUG: Request data received ->", request.data)

            product_data = request.data.get('products', [])  # [{"id": 1, "quantity": 2}]
            food_ids = request.data.get('food_ids', [])
            accompaniment_ids = request.data.get('accompaniment_ids', [])
            phone_number = request.data.get("phone_number")
            amount = request.data.get("amount")

            # Fetch products, foods, accompaniments
            product_ids = [p['id'] for p in product_data]
            products = Product.objects.filter(id__in=product_ids)
            foods = Food.objects.filter(id__in=food_ids)
            accompaniments = Accompaniment.objects.filter(id__in=accompaniment_ids)

            if len(products) != len(product_ids):
                return Response({'error': 'Some product IDs are invalid.'}, status=400)

            # Calculate preparation time
            max_product_time = products.aggregate(Max('preparation_time'))['preparation_time__max'] or 0
            max_food_time = foods.aggregate(Max('preparation_time'))['preparation_time__max'] or 0
            max_accomp_time = accompaniments.aggregate(Max('preparation_time'))['preparation_time__max'] or 0
            preparation_time = max(max_product_time, max_food_time, max_accomp_time)

            # Create the order first
            order = Order.objects.create(
                user=request.user,
                total_price=0,  # will calculate after adding items
                payment_status="pending",
                preparation_time=preparation_time
            )

            # Create OrderItems and reduce stock
            total_price = 0
            for item_data in product_data:
                product = Product.objects.get(id=item_data["id"])
                quantity = item_data.get("quantity", 1)
                order_item = OrderItem(order=order, product=product, quantity=quantity)
                try:
                    order_item.full_clean()  # validate stock
                    order_item.save()
                    # Reduce stock
                    product.stock -= quantity
                    product.save()
                    total_price += product.price * quantity
                except ValidationError as e:
                    order.delete()  # rollback the order
                    return Response({"error": str(e)}, status=400)

            # Assign foods and accompaniments
            order.foods.set(foods)
            order.accompaniments.set(accompaniments)

            # Update total price
            order.total_price = total_price
            order.save(update_fields=["total_price"])

            # Trigger payment
            payment_response = PaymentView.deposit(request.user, phone_number, int(amount))
            if isinstance(payment_response, Response) and payment_response.status_code == 200:
                payment_id = payment_response.data.get("payment_id")
                payment_instance = Payment.objects.get(id=payment_id)
                order.order_payment = payment_instance
                order.payment_status = payment_instance.status
                order.save()

            serializer = OrderSerializer(order)
            return Response(serializer.data, status=201)

        except Exception as e:
            print("ERROR:", str(e))
            return Response({'error': str(e)}, status=500)

 

        


class OrderDetailView(generics.RetrieveUpdateAPIView):
    # queryset=Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)
class ListOrderView(generics.ListAPIView):
    queryset=Order.objects.all().order_by('-created_at')
    serializer_class=OrderSerializer
    permissions_classes=[permissions.IsAdminUser]