from django.urls import path
from .views import (MessageViewSet,ChatRoomViewSet,FAQsView,SearchFaqs,ChatRoomListCreateView,
    ChatRoomRetrieveDestroyView,
    MessageListCreateView,
    MessageRetrieveUpdateDestroyView,)
urlpatterns=[
    path('',MessageViewSet.as_view()),
    path('<uuid:chat_room_id>',MessageViewSet.as_view()),
    path('room/',ChatRoomViewSet.as_view()),
    path('room/<uuid:chat_room_id>/messages/',MessageViewSet.as_view()),
    path("chat-rooms/", ChatRoomListCreateView.as_view(), name="chatroom-list-create"),
    path("chat-rooms/<uuid:pk>/", ChatRoomRetrieveDestroyView.as_view(), name="chatroom-detail"),
    path("chat-rooms/<uuid:chat_room_id>/messages/", MessageListCreateView.as_view(), name="message-list-create"),
    path("messages/<uuid:pk>/", MessageRetrieveUpdateDestroyView.as_view(), name="message-detail"),
    path('search-faqs',SearchFaqs.as_view()),
    path('faqs',FAQsView.as_view()),
]