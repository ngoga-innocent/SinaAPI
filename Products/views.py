from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from rest_framework import generics, permissions,status,serializers
from decimal import Decimal
from .models import Product, ProductCategory,ShopCategory,FoodCategory, Food,Order,Accompaniment
from .serializers import ProductSerializer,ProductCategorySerializer,ShopCategorySerializer,FoodCategorySerializer,OrderSerializer
from Auths.models import User
from Payments.views import PaymentView
from Payments.models import Payment
from django.db.models import Max
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
        try:
            food_categories = FoodCategory.objects.all()
            serializer=FoodCategorySerializer(food_categories, many=True, context={"request": request})
            return Response({"data": serializer.data}, status=200)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=500)
class OrderCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self,request):
        orders=Order.objects.filter(user=request.user)
        serializer=OrderSerializer(orders,many=True,context={"request": request})
        return Response({"data": serializer.data}, status=200)
    def post(self, request):
        try:
            print("DEBUG: Request data received ->", request.data)
            print("DEBUG: User ->", request.user.id)

            # ✅ Extract IDs from request
            product_ids = request.data.get('product_ids', [])
            food_ids = request.data.get('food_ids', [])
            accompaniment_ids = request.data.get('accompaniment_ids', [])
            phone_number = request.data.get("phone_number")
            amount=request.data.get("amount")
            # ✅ Fetch products, foods, and accompaniments
            products = Product.objects.filter(id__in=product_ids)
            foods = Food.objects.filter(id__in=food_ids)
            accompaniments = Accompaniment.objects.filter(id__in=accompaniment_ids)

            # ❌ Validate IDs
            if len(products) != len(product_ids):
                return Response({'error': 'Some product IDs are invalid.'}, status=status.HTTP_400_BAD_REQUEST)
            if len(foods) != len(food_ids):
                return Response({'error': 'Some food IDs are invalid.'}, status=status.HTTP_400_BAD_REQUEST)
            if len(accompaniments) != len(accompaniment_ids):
                return Response({'error': 'Some accompaniment IDs are invalid.'}, status=status.HTTP_400_BAD_REQUEST)

            # ✅ Calculate total price
            total_price = sum(product.price for product in products) + \
                          sum(food.price for food in foods) + \
                          sum(accompaniment.price for accompaniment in accompaniments)

            print("DEBUG: Total Price ->", total_price)

            # ✅ Calculate preparation time (maximum from all items)
            max_product_time = products.aggregate(Max('preparation_time'))['preparation_time__max'] or 0
            max_food_time = foods.aggregate(Max('preparation_time'))['preparation_time__max'] or 0
            max_accompaniment_time = accompaniments.aggregate(Max('preparation_time'))['preparation_time__max'] or 0
            preparation_time = max(max_product_time, max_food_time, max_accompaniment_time)

            print("DEBUG: Estimated Preparation Time ->", preparation_time, "minutes")

            # ✅ Get User
            try:
                user = User.objects.get(id=request.user.id)
            except User.DoesNotExist:
                return Response({"error": "User does not exist"}, status=400)

            # ✅ Create the order
            order = Order.objects.create(
                user=user,
                total_price=Decimal(amount),
                payment_status="pending",
                preparation_time=preparation_time  # Assign computed prep time
            )

            # ✅ Set relationships
            order.products.set(products)
            order.foods.set(foods)
            order.accompaniments.set(accompaniments)

            # ✅ Trigger Payment
            payment_response = PaymentView.deposit(request.user, phone_number, int(amount))
            if isinstance(payment_response, Response) and payment_response.status_code == 200:
                payment_id = payment_response.data.get("payment_id")  # Extract payment ID
                print("DEBUG: Payment ID ->", payment_id)
                
                # Fetch payment instance
                payment_instance = Payment.objects.get(id=payment_id)
                
                # ✅ Assign payment to order
                order.order_payment = payment_instance
                order.payment_status = payment_instance.status  # Sync status
                order.save()
            print("DEBUG: Order Created ->", order.id, "for user", order.user.id)

            # ✅ Serialize and return the response
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("ERROR:", str(e))
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

        


class OrderDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
        