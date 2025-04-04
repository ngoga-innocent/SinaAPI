from rest_framework import serializers
from .models import Message,ChatRoom,MessageReadStatus
from Auths.models import User
from Auths.serializers import UserSerializer
class MessageSerializer(serializers.ModelSerializer):
    sender_details = UserSerializer(read_only=True,source='sender')
    receiver_details = UserSerializer(read_only=True,source='receiver')
    
    class Meta:
        model = Message
        fields = ['id', 'chat_room', 'sender', 'receiver', 'sender_details', 'receiver_details', 'message_type', 'message', 'file', 'status', 'created_at', 'updated_at']
        read_only_fields = ['sender', 'created_at', 'updated_at']
class ChatRoomSerializer(serializers.ModelSerializer):
    unread_messages_count = serializers.SerializerMethodField()
    messages = MessageSerializer(source="message_set", many=True, read_only=True)
    
    client_data = UserSerializer(read_only=True, source='client')  # Re-added client_data for user info serialization
    last_message_details = MessageSerializer(read_only=True, source="last_message")

    class Meta:
        model = ChatRoom
        fields = ["id","client","client_data","messages", "last_message", "last_message_details", "unread_messages_count", "created_at", "updated_at"]

    def get_unread_messages_count(self, obj):
        request = self.context.get('request', None)  # Get request safely
        print("Request in serializer:", request)  # Debug request
        print("User:", getattr(request, 'user', None))  # Debug user
        print("ChatRoom:", obj)

        if request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            print("count message user",user)
            # Filter based on user type
            filters = {"chat_room": obj}
            if user.is_staff:
                filters["staff_read"] = False  # Count unread messages for staff
            else:
                filters["is_read"] = False  # Count unread messages for regular users

            return MessageReadStatus.objects.filter(**filters).count()

        return 0  # Default to 0 if request/user is missing
    # Default to 0 if request is None or unauthenticated



