"""chat URL Configuration"""
from django.urls import path, include
from .views import (
    ChatsView,
    NewChat,
    DeleteChat,
    HomePageRedirect,
)

app_name = 'chats'

chat_patterns = [
    path('', ChatsView.as_view(), name='chats_list'),
    path('new_chat/', NewChat.as_view(), name='new_chat'),
    path('delete/<int:pk>', DeleteChat.as_view(), name="delete_chat"),
]

urlpatterns = [
    path('', HomePageRedirect.as_view(), name='home'),
    path('chats/<int:user_id>/', include(chat_patterns)),
    path('chats/<int:user_id>/<int:chat_id>/', include('chat_messages.urls')),
]
