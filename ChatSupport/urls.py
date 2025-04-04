from django.urls import path
from .views import MessageViewSet,ChatRoomViewSet
urlpatterns=[
    path('',MessageViewSet.as_view()),
    path('<uuid:chat_room_id>',MessageViewSet.as_view()),
    path('room/',ChatRoomViewSet.as_view()),
    path('room/<uuid:chat_room_id>/messages/',MessageViewSet.as_view())
]