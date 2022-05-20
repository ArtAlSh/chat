from django.test import TestCase, modify_settings
from django.shortcuts import reverse
from django.contrib.auth.models import User
from chats.models import Chat, ListOfChats
from .models import Message


class SetUpMsg(TestCase):
    """
    Class represent settings and
    base methods fot testing 'chat_messages' app
    """
    user_password = '123'

    def setUp(self):
        username1 = 'user1'
        username2 = 'user2'
        # create two users
        self.user1 = self.create_user(username1)
        self.user2 = self.create_user(username2)
        # create users chat
        ListOfChats.objects.create(user=self.user1, to_user=self.user2)
        self.chat = Chat.objects.all().get()
        # authenticate user1 by default
        self.authenticate_user(self.user1)

    def create_user(self, username):
        user = User.objects.create_user(
            username=username,
            password=self.user_password
        )
        return user

    def authenticate_user(self, user: User):
        users_list = User.objects.all()
        if user in users_list:
            self.client.login(username=user.username, password=self.user_password)

    def create_msg(self, user: User, text='Hello', test=True) -> Message:
        """
        Create message
        If 'test' is "True' return message, 'False' return response
        """
        # count number of messages in chat
        msg_num = self.chat.message_set.count()
        new_msg_url = reverse(
            'chats:new_message',
            kwargs={'user_id': user.id, 'chat_id': self.chat.id}
        )
        response = self.client.post(new_msg_url, data={'text': text}, follow=True)
        if test:
            # check new message in list
            self.assertEqual(response.context_data['messages_list'].count(), msg_num + 1)
            return response.context_data['messages_list'].last()
        else:
            return response


class MessageViewTest(SetUpMsg):
    """Class for test MessageView"""

    def test_returned_message_page(self):
        """Check message page response"""
        msg_url = reverse(
            'chats:message_view',
            kwargs={'user_id': self.user1.id, 'chat_id': self.chat.id}
        )
        response = self.client.get(msg_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['messages_list'].count(), 0)
        self.assertEqual(response.context_data['chats_list'].count(), 1)
        self.assertIn('message_list.html', response.template_name)

    def test_status_not_existing_chat(self):
        """Check status code for doesn't exist chat"""
        msg_url = reverse(
            'chats:message_view',
            kwargs={
                'user_id': self.user1.id,
                'chat_id': self.chat.id + 1,
            }
        )
        response = self.client.get(msg_url, follow=True)
        self.assertIn(response.status_code, [403, 404])


class NewMessageTest(SetUpMsg):
    """Class for test NewMessage"""

    def test_new_message(self):
        """Create messages in chat between users and check messages in users chats"""
        # create message by user1
        self.create_msg(self.user1)
        # create message by user2
        self.authenticate_user(self.user2)
        self.create_msg(self.user2)

    def test_new_message_prohibitions(self):
        """User can't create another user's message"""
        # user1 authenticated bu default
        response = self.create_msg(self.user2, test=False)
        # count message in user's chat
        self.assertEqual(response.status_code, 403)


class DeleteMessageTest(SetUpMsg):
    """Class for test DeleteMessage"""

    def test_delete_message(self):
        """Create and delete message"""
        msg = self.create_msg(self.user1)
        del_msg_url = reverse(
            'chats:delete_message',
            kwargs={'user_id': self.user1.id, 'chat_id': self.chat.id, 'pk': msg.pk}
        )
        response = self.client.get(del_msg_url, follow=True)
        self.assertEqual(response.context_data['messages_list'].count(), 0)

    def test_delete_message_prohibitions(self):
        """User can't delete another user's message"""
        msg = self.create_msg(self.user1)
        # self.client.login(username=self.username2, password=self.password)
        self.authenticate_user(self.user2)
        del_msg_url = reverse(
            'chats:delete_message',
            kwargs={'user_id': self.user1.id, 'chat_id': self.chat.id, 'pk': msg.pk}
        )
        response = self.client.get(del_msg_url, follow=True)
        self.assertEqual(response.status_code, 403)


class UpdateMessageTest(SetUpMsg):
    """Class for test UpdateMessage"""

    def setUp(self):
        super().setUp()
        # create message
        self.base_msg_text = 'Hello'
        self.msg = self.create_msg(self.user1, text=self.base_msg_text)

    def test_update_msg(self):
        """test to edit message"""
        # user1 authenticated by default
        # get update message
        update_msg_url = reverse(
            'chats:update_message',
            kwargs={
                'user_id': self.user1.id,
                'chat_id': self.chat.id,
                'message_id': self.msg.id
            }
        )
        response = self.client.get(update_msg_url, follow=True)
        msg_form = response.context_data['message_form']
        msg_form_url = response.context_data['message_form_url']
        msg_text = msg_form.initial['text']
        self.assertEqual(msg_text, self.base_msg_text)
        self.assertURLEqual(msg_form_url, update_msg_url)
        # edit and update message
        edit_msg_text = 'Hello, world!'
        response = self.client.post(update_msg_url, data={'text': edit_msg_text}, follow=True)
        self.msg = Message.objects.get(id=self.msg.id)
        self.assertEqual(self.msg.text, edit_msg_text)

    def test_update_msg_prohibitions(self):
        """User cant edit other users messages"""
        self.authenticate_user(self.user2)
        update_msg_url = reverse(
            'chats:update_message',
            kwargs={
                'user_id': self.user1.id,
                'chat_id': self.chat.id,
                'message_id': self.msg.id
            }
        )
        response = self.client.get(update_msg_url, follow=True)
        self.assertEqual(response.status_code, 403)
