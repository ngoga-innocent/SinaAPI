from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status,generics
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
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from rest_framework import status, permissions
from django.contrib.auth import logout
from .models import Notification,DeviceToken
from .serializers import NotificationSerializer
from django.db import models
from rest_framework.decorators import api_view,permission_classes
# from rest_framework_simplejwt.tokens import RefreshToken
User = get_user_model()
# Create your views here.
class UserView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(
            {"detail": "GET method not allowed. Use POST to register."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
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




class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)  # clears the session
        return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)

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
class RequestPasswordResetView(APIView):
    def get(self,request):
        return render(request,'reset_password.html')
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            reset_link = f"https://sina-gerard.onrender.com/auth/reset-password?uid={uid}&token={token}"

            send_mail(
                subject="Password Reset Request",
                message=f"Click the link to reset your password: {reset_link}",
                from_email="no-reply@yourdomain.com",
                recipient_list=[email],
            )
            return Response({'message': 'Password reset email sent'}, status=200)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
class PasswordResetConfirmView(APIView):
    def post(self, request):
        uid = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)

            if PasswordResetTokenGenerator().check_token(user, token):
                user.set_password(new_password)
                user.save()
                return Response({'message': 'Password reset successful'}, status=200)
            else:
                return Response({'error': 'Invalid or expired token'}, status=400)

        except Exception as e:
            return Response({'error': 'Something went wrong'}, status=400)
class NotificationListCreateView(generics.ListCreateAPIView):
    queryset = Notification.objects.all().order_by("-created_at")
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            user = self.request.user
            return Notification.objects.filter(
                models.Q(notification_type="all") | 
                models.Q(notification_type="user", user=user)
            ).order_by("-created_at")
        except Exception as e:
            print(f"Error in get_queryset: {str(e)}")  # Add logging
            return Notification.objects.none()  # Return empty queryset on error

class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            # Staff can only see notifications intended for staff or for all
            return Notification.objects.filter(
                models.Q(notification_type="staff") |
                models.Q(notification_type="all")
            )
        # Regular user: only their notifications or all
        return Notification.objects.filter(
            models.Q(notification_type="user", user=user) |
            models.Q(notification_type="all")
        )

    def perform_update(self, serializer):
        notification = self.get_object()
        if notification.notification_type == "user" and notification.user != self.request.user:
            raise PermissionError("You cannot update notifications that don't belong to you")
        serializer.save()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_push_token(request):
    token = request.data.get("expo_push_token")
    print(token)
    if not token:
        return Response({"error": "Missing token"}, status=status.HTTP_400_BAD_REQUEST)

    # request.user is the authenticated user
    user = request.user  

    DeviceToken.objects.update_or_create(
        user=user, defaults={"expo_push_token": token}
    )

    return Response({"success": True}, status=status.HTTP_200_OK)
