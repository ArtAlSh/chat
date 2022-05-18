from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


class Chat(models.Model):
    id = models.BigAutoField(primary_key=True)

    def delete(self, using=None, keep_parents=False):
        """Delete this chat and all entries in ListOfChats"""
        super().delete(using, keep_parents)
        self._delete_from_users_list()

    def _delete_from_users_list(self):
        """Delete all entries in ListOfChats"""
        chats_list = self.listofchats_set.filter(chat_id=self.id)
        for chat in chats_list:
            chat.delete()

    def users_list(self):
        users = []
        for chat_in_list in self.listofchats_set.all():
            users.append(chat_in_list.user)
        return users

    def __str__(self):
        return f"chat_id={self.id}"


class ListOfChats(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.SET(get_user_model()),
        related_name='chatslist',
    )
    to_user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='chat_to_user',
    )
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.to_user.username

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        """Check chat in users exist chats. Create chat and entries in ListOfChats if chat doesn't exist"""
        # check chat in user's exist chats
        check_in_user_list = ListOfChats.objects.filter(user=self.user, to_user=self.to_user)
        check_in_to_user_list = ListOfChats.objects.filter(user=self.to_user, to_user=self.user)

        if check_in_user_list.count():
            pass
        elif (not check_in_user_list.count()) and (not check_in_to_user_list.count()):
            self.chat = self._create_chat()
            super().save(force_insert, force_update, using, update_fields)
            self._add_in_to_user_list()
        elif check_in_to_user_list.count():
            chat_in_list = check_in_to_user_list.get()
            self.chat = chat_in_list.chat
            super().save(force_insert, force_update, using, update_fields)

    def delete(self, using=None, keep_parents=False):
        """Delete the Chat if it is the last entry in ListOfChat"""
        entries_num = self.chat.listofchats_set.all().count()
        if entries_num == 1:
            self.chat.delete()
        else:
            super().delete(using, keep_parents)

    def _create_chat(self):
        """Create chat"""
        chat = Chat.objects.create()
        chat.save()
        return chat

    def _add_in_to_user_list(self):
        """Create a entry in to_user's ListOfChats"""
        chat_list = ListOfChats.objects.create(
            user=self.to_user,
            to_user=self.user,
        )
        chat_list.save()
