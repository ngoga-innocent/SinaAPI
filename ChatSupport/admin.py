from django.contrib import admin
from .models import Message, ChatRoom,MessageReadStatus

# Inline configuration for Message
class MessageInline(admin.StackedInline):
    model = Message
    extra = 0

# Register ChatRoom model in the admin
@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_message', 'updated_at', 'created_at')
    list_filter = ('created_at',)
    
    # Inline configuration to show Messages within ChatRoom
    inlines = [MessageInline]

# Register Message model in the admin
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'created_at', 'updated_at')  # Ensure 'message' is the correct field name
    list_filter = ('created_at',)   
@admin.register(MessageReadStatus)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'is_read','staff_read', 'read_at')  # Ensure 'message' is the correct field name
    list_filter = ('read_at','is_read',)   