from rest_framework import viewsets, status,generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import ChatRoom, Message,MessageReadStatus,FAQs
from .serializers import MessageSerializer,ChatRoomSerializer,FAQsSerializer
from rest_framework.views import APIView
from django.utils.timezone import now,datetime
from rest_framework.decorators import api_view
import traceback
class MessageViewSet(APIView):
    """Handles sending, retrieving, updating, and deleting messages."""
    permission_classes = [IsAuthenticated]

    # ✅ LIST MESSAGES IN A CHAT ROOM
    def get(self, request, chat_room_id=None):
        """Retrieve all messages in a chat room."""
        print("Retreiving messages")
        # Ensure chat_room_id is valid
        if not chat_room_id:
            return Response({"error": "Chat room ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
        print("Chat room updated_at:", chat_room.updated_at)

        # Ensure the user is authenticated
        if not request.user or request.user.is_anonymous:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        # Check if the user is part of the chat
        # if not chat_room.users.filter(id=request.user.id).exists():
        #     return Response({"error": "You are not a participant in this chat."}, status=status.HTTP_403_FORBIDDEN)

        try:
            messages = Message.objects.filter(chat_room=chat_room).order_by('created_at')
            # print("Room messages SQL query:", messages.query)  # Debugging
            chat_room_Messages_Status=MessageReadStatus.objects.filter(chat_room=chat_room)
            print(chat_room_Messages_Status)
            for message in chat_room_Messages_Status:
                if request.user.is_staff:
                    message.staff_read=True
                else:
                    message.is_read=True
                message.save()
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            print("Error retrieving messages:", e)
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # ✅ RETRIEVE SINGLE MESSAGE
    def retrieve(self, request, pk=None):
        """Retrieve a single message."""
        message = get_object_or_404(Message, id=pk)

        # Ensure user is part of the chat
        if request.user not in message.chat_room.participants.all():
            return Response({"error": "You are not allowed to view this message."}, status=status.HTTP_403_FORBIDDEN)

        serializer = MessageSerializer(message)
        return Response(serializer.data)

    # ✅ SEND MESSAGE (CREATE)
    def post(self, request, chat_room_id=None):
        """Send a new message in a chat room."""
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id)

        if not request.user or not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data.copy()
        data["sender"] = request.user.id  # Ensure sender is set

        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            message = serializer.save(sender=request.user)  # Explicitly set sender as a user object

            # ✅ Update last message in ChatRoom
            ChatRoom.objects.filter(id=chat_room_id).update(last_message=message,updated_at=datetime.now())

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # ✅ UPDATE MESSAGE (EDIT)
    def update(self, request, pk=None):
        """Allows sender to edit their message."""
        message = get_object_or_404(Message, id=pk)

        # Ensure only sender can edit
        if request.user != message.sender:
            return Response({"error": "You can only edit your own messages."}, status=status.HTTP_403_FORBIDDEN)

        serializer = MessageSerializer(message, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ✅ DELETE MESSAGE
    def destroy(self, request, pk=None):
        """Allows sender to delete their message."""
        message = get_object_or_404(Message, id=pk)

        # Ensure only sender can delete
        if request.user != message.sender:
            return Response({"error": "You can only delete your own messages."}, status=status.HTTP_403_FORBIDDEN)

        message.delete()
        return Response({"message": "Message deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
class ChatRoomViewSet(APIView):
    permission_classes = [IsAuthenticated]

    # ✅ LIST CHAT ROOMS
    def get(self, request):
        
        
        if request.user.is_anonymous:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            print("User is staff:", request.user.is_staff)

            if request.user.is_staff:
                chat_rooms = ChatRoom.objects.all().order_by("-updated_at")
            else:
                chat_rooms = ChatRoom.objects.filter(client=request.user).order_by("-updated_at")
            
            # print("Chat rooms found:", chat_rooms.count())  # Debugging
            if not chat_rooms.exists():
                return Response({"message": "No chat rooms found."}, status=status.HTTP_404_NOT_FOUND)

            try:
                serializer = ChatRoomSerializer(chat_rooms, many=True, context={'request': request})  # Ensure request is passed
                print("Serialized chat rooms:", serializer.data)
                return Response(serializer.data, status=200)
            
            except Exception as e:
                # print(f"Error serializing chat rooms: {e}")
                print(f"Detailed error: {traceback.format_exc()}")
                return Response({"error": "Error serializing chat rooms"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            # print(f"Error retrieving chat rooms: {e}")
            print(f"Detailed error: {traceback.format_exc()}")
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ✅ RETRIEVE A CHAT ROOM (WITH MESSAGES)
    def retrieve(self, request, pk=None):
        """Retrieve a single chat room along with its messages."""
        chat_room = get_object_or_404(ChatRoom, id=pk)

        # Ensure the user is a participant in the chat room
        if request.user not in chat_room.participants.all():
            return Response({"error": "You are not a participant in this chat room."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ChatRoomSerializer(chat_room)
        return Response(serializer.data)

    # ✅ CREATE OR RETURN EXISTING CHAT ROOM
    def post(self, request):
        """Ensure each customer has only one support chat room."""
        customer = request.user  # The authenticated customer

        # Check if the customer already has a chat room
        existing_chat_room = ChatRoom.objects.filter(client=customer).first()

        if existing_chat_room:
            # ✅ If the room exists, return it instead of creating a new one
            serializer = ChatRoomSerializer(existing_chat_room)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Create a new chat room for the customer
        if request.user.is_staff:
            return Response("You can't create the chat with staff account",status=401)
        chat_room = ChatRoom.objects.create(
            client=request.user
        )
        # chat_room.participants.add(customer)  # Only add the customer
        # chat_room.save()

        serializer = ChatRoomSerializer(chat_room)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ✅ DELETE A CHAT ROOM
    def destroy(self, request, pk=None):
        """Delete a chat room."""
        chat_room = get_object_or_404(ChatRoom, id=pk)

        # Only allow deletion if the user is part of the chat room
        if request.user not in chat_room.participants.all():
            return Response({"error": "You cannot delete this chat room."}, status=status.HTTP_403_FORBIDDEN)

        chat_room.delete()
        return Response({"message": "Chat room deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
@api_view(['POST'])
def mark_messages_as_read(request, room_id):
    """Mark all unread messages in a chat room as read for the current user"""
    chat_room = ChatRoom.objects.filter(id=room_id).first()
    if not chat_room:
        return Response({"error": "Chat room not found"}, status=status.HTTP_404_NOT_FOUND)

    unread_messages = Message.objects.filter(chat_room=chat_room).exclude(sender=request.user)

    for message in unread_messages:
        read_status, created = MessageReadStatus.objects.get_or_create(
            message=message,
            user=request.user
        )
        read_status.is_read = True
        read_status.read_at = now()
        read_status.save()

    return Response({"message": "Messages marked as read"}, status=status.HTTP_200_OK)
class FAQsView(APIView):
    def get(self, request):
        faqs = FAQs.objects.all()
        serializer=FAQsSerializer(faqs,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
class SearchFaqs(APIView):
    def get(self,request):
        query=request.GET.get('query')
        faqs=FAQs.objects.filter(question__icontains=query)
        serializer=FAQsSerializer(faqs,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
# Generic Views
class ChatRoomListCreateView(generics.ListCreateAPIView):
    """List all chat rooms or create a new one for a customer"""
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ChatRoom.objects.all().order_by("-updated_at")
        return ChatRoom.objects.filter(client=user).order_by("-updated_at")

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_staff:
            raise PermissionError("Staff cannot create chat rooms")
        # Ensure only one room per customer
        existing_room = ChatRoom.objects.filter(client=user).first()
        if existing_room:
            return existing_room
        serializer.save(client=user)


class ChatRoomRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    """Retrieve or delete a single chat room"""
    serializer_class = ChatRoomSerializer
    permission_classes = [IsAuthenticated]
    queryset = ChatRoom.objects.all()
    lookup_field = "pk" 
    def delete(self, request, *args, **kwargs):
        room = self.get_object()
        if request.user not in room.participants.all():
            return Response({"error": "You cannot delete this chat room."}, status=status.HTTP_403_FORBIDDEN)
        return super().delete(request, *args, **kwargs)

# -------------------------------
# Message Generic Views
# -------------------------------
class MessageListCreateView(generics.ListCreateAPIView):
    """List messages in a chat room or send a new message"""
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chat_room_id = self.kwargs.get("chat_room_id")
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
        return Message.objects.filter(chat_room=chat_room).order_by('created_at')

    def perform_create(self, serializer):
        chat_room_id = self.kwargs.get("chat_room_id")
        chat_room = get_object_or_404(ChatRoom, id=chat_room_id)
        message = serializer.save(sender=self.request.user, chat_room=chat_room)
        # Update last_message and updated_at
        ChatRoom.objects.filter(id=chat_room_id).update(last_message=message, updated_at=now())


class MessageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a single message"""
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    queryset = Message.objects.all()

    def update(self, request, *args, **kwargs):
        message = self.get_object()
        if message.sender != request.user:
            return Response({"error": "You can only edit your own messages."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        message = self.get_object()
        if message.sender != request.user:
            return Response({"error": "You can only delete your own messages."}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)