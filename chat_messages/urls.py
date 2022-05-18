"""chat URL Configuration"""
from django.urls import path
from .views import (
    MessageView,
    NewMessage,
    DeleteMessage,
    UpdateMessage,
)

urlpatterns = [
    path('', MessageView.as_view(), name='message_view'),
    path('new_message/', NewMessage.as_view(), name='new_message'),
    path('delete_message/<int:pk>', DeleteMessage.as_view(), name='delete_message'),
    path('update_message/<int:message_id>', UpdateMessage.as_view(), name='update_message'),
]
