from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import RegisterUserSerializer,UserSerializer
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.core.files.storage import default_storage
from django.db.models import Q
User = get_user_model()
# Create your views here.
class UserView(APIView):
    def get(self, request, *args, **kwargs):
        pass
    def post(self, request, *args, **kwargs):
        return self.Register(request)
    def Register(self, request, *args, **kwargs):
        serializer = RegisterUserSerializer(data=request.data)
        password = request.data.get('password')

        if password:
            try:
                validate_password(password)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            user = serializer.save()
            user.set_password(password)
            user.save()
            return Response({"data": serializer.data}, status=201)
        else:
            # Convert serializer.errors into a plain string message
            error_messages = "\n".join(
                [f"{key}: {', '.join(map(str, value))}" for key, value in serializer.errors.items()]
            )
            return Response({"error": error_messages}, status=400)

class LoginView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        if not phone_number or not password:
            return Response({"error": "Phone number and password are required"}, status=status.HTTP_400_BAD_REQUEST)  # missing required field(s)
        try:
            user = User.objects.get(Q(phone_number=phone_number) | Q(email=phone_number))
            if not user:
                return Response({"error": "Incorrect Phone number please Try again later"}, status=status.HTTP_404_NOT_FOUND)
            if not user.check_password(password):
                return Response({"error": "Incorrect password"}, status=status.HTTP_401_UNAUTHORIZED)

            user = authenticate(phone_number=phone_number, password=password)
            if user:
                user_data=UserSerializer(user).data
                token, created = Token.objects.get_or_create(user=user)
                # refresh = RefreshToken.for_user(user)
                return Response({
                    "accessToken": token.key,
                    
                    "user_data": user_data
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(e)
            return Response({"error": "Incorrect Phone number please Try again"}, status=status.HTTP_404_NOT_FOUND)
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response({"user_data":serializer.data})    
    def put(self, request):
        """Partially update user profile fields"""
        try:
            user = request.user
            serializer = UserSerializer(user, data=request.data, partial=True)  # Partial update
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Profile updated successfully", "user_data": serializer.data}, status=status.HTTP_200_OK)
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(e)
            return Response(
                {"error": "Something went wrong", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    def patch(self, request):
        """Change user password without using a serializer"""
        user = request.user
        data = request.data

        # Extract old and new password
        old_password = data.get("old_password")
        new_password = data.get("new_password")
        # confirm_password = data.get("confirm_password")

        # Validate required fields
        if not old_password or not new_password:
            return Response(
                {"error": "All fields (old_password, new_password) are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if old password is correct
        if not user.check_password(old_password):
            return Response({"error": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if new password matches confirmation
        # if new_password != confirm_password:
        #     return Response({"error": "New passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        # Change password and save
        user.set_password(new_password)
        user.save()

        return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)    