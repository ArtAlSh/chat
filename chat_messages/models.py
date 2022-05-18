# Django's libs
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
# other app's libs
from chats.models import Chat


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='msg_from')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='msg_to')
    date = models.DateTimeField(auto_now_add=True)
    text = models.TextField()

    def get_absolute_url(self):
        kwargs = {
            "user_id": self.from_user.id,
            "chat_id": self.chat.id,
        }
        return reverse('chat:message_view', kwargs=kwargs)

    def users_list(self):
        users = (
            self.from_user,
            self.to_user,
        )
        return users
