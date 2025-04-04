from django.db import models
import uuid
from Auths.models import User
from django.utils.timezone import now
class ChatRoom(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(User, related_name="chat_rooms", on_delete=models.CASCADE)  # Changed to ForeignKey2
    last_message = models.OneToOneField(
        'Message', on_delete=models.SET_NULL, null=True, blank=True, related_name='last_message_of_chat'
    )
    updated_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ChatRoom {self.id} - {self.client.phone_number}"

    class Meta:
        verbose_name = 'ChatRoom'
        verbose_name_plural = 'ChatRooms'
        ordering = ['-updated_at']


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE,related_name='room')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages", null=True, blank=True)

    MESSAGE_TYPES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('file', 'File'),
        ('voice', 'Voice Note'),
    )
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    message = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to="chat_uploads/", null=True, blank=True)

    MESSAGE_STATUS = (
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
    )
    status = models.CharField(max_length=10, choices=MESSAGE_STATUS, default='sent')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver or 'Group'}: {self.message[:30]}"
    def save(self, *args, **kwargs):
        """Auto-create read status for sender and receiver"""
        is_new_message = self._state.adding  # Check if it's a new message
        super().save(*args, **kwargs)

        if is_new_message:
            # Mark message as read for the sender
            MessageReadStatus.objects.get_or_create(
                message=self,
                user=self.sender,
                chat_room=self.chat_room,
                defaults={
                    "is_read": not self.sender.is_staff,  # If staff, mark as read; otherwise, False
                    "staff_read": self.sender.is_staff,
                    "read_at": now() if self.sender.is_staff else None,
                }
            )

            # Mark message as unread for the receiver
            if self.receiver:
                MessageReadStatus.objects.get_or_create(
                    message=self,
                    user=self.receiver,
                    defaults={"is_read": False, "staff_read": False}
                )
class MessageReadStatus(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="read_status")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_room=models.ForeignKey(ChatRoom,on_delete=models.CASCADE,related_name='chat_room_read_status',null=True)
    is_read = models.BooleanField(default=False)
    staff_read=models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} read {self.message.id} at {self.read_at}"

    class Meta:
        verbose_name_plural='Message Statuses'
        unique_together = ('message', 'user')  # Ensure each user has only one read status per message
