from django.test import TestCase, TransactionTestCase, Client
from django.urls import reverse, reverse_lazy
from django.contrib.auth.models import User
from .models import Chat, ListOfChats


class ChatViewTest(TestCase):
    def setUp(self):
        """Create user"""
        self.username = 'test_user'
        self.user_password = '123'
        self.user = User.objects.create_user(
            username=self.username,
            password=self.user_password
        )

    def test_redirect_page_for_not_auth_user(self):
        """Not authenticated should redirect to login page"""
        # Check that first page is login page
        response = self.client.get('/')
        response_url = response.url.split('?')[0] if '?' in response.url else response.url
        self.assertURLEqual(response_url, reverse_lazy('accounts:login'))
        # check that user can't go to the chats page before authenticating
        user_chat_page_url = reverse(
            'chats:chats_list',
            kwargs={'user_id': self.user.pk}
        )
        response = self.client.get(user_chat_page_url)
        response_url = response.url.split('?')[0] if '?' in response.url else response.url
        self.assertURLEqual(response_url, reverse_lazy('accounts:login'))

    def test_redirect_page_for_auth_user(self):
        """User redirect to the chats page after authentication"""
        # Authenticate user
        auth_url = reverse_lazy('accounts:login')
        response = self.client.post(
            path=auth_url,
            data={'username': self.username, 'password': self.user_password},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertURLEqual(
            response.request['PATH_INFO'],
            reverse('chats:chats_list', kwargs={'user_id': self.user.id})
        )

    def test_forbidden_other_users_pages(self):
        """User can see only his chats page"""
        # Create second user
        user2 = User.objects.create_user(username='test_user2', password='123')
        # Authenticate user1
        self.client.login(username=self.username, password=self.user_password)
        # try get to the user2's chats list
        response = self.client.get(reverse('chats:chats_list', kwargs={'user_id': user2.pk}))
        self.assertEqual(response.status_code, 403)
        # try to get to doesn't exist chat
        response = self.client.get(reverse('chats:chats_list', kwargs={'user_id': (user2.pk + 1)}))
        self.assertEqual(response.status_code, 403)


class ChatModelTest(TransactionTestCase):
    """Testing Chat and ListOfChat behaviors"""

    def setUp(self):
        """Create users and chats for them"""
        self.user1 = User.objects.create(username='Nastya', password='123')
        self.user2 = User.objects.create(username='Julia', password='123')
        ListOfChats.objects.create(user=self.user1, to_user=self.user2)

    def test_create_chat(self):
        """
        ListOfChat model should create two entries
        in ListOfChats for each user and one Chat model for them
        """
        self.assertEqual(ListOfChats.objects.count(), 2)
        self.assertEqual(Chat.objects.count(), 1)
        # check that all users have one chat
        chat1 = ListOfChats.objects.get(user=self.user1).chat
        chat2 = ListOfChats.objects.get(user=self.user2).chat
        self.assertEqual(chat1, chat2)

    def test_delete_chat(self):
        """
        Chat should be deleted when deleted all entries with the Chat in ListOfChat.
        Every user can delete chat in own ListOfChat and back to the Chat when add again.
        """
        # delete entry in user1's ChatOfList and check that chat exist already
        chat1 = ListOfChats.objects.get(user=self.user1)
        chat1.delete()
        self.assertEqual(ListOfChats.objects.count(), 1)
        self.assertEqual(Chat.objects.count(), 1)
        self.assertEqual(ListOfChats.objects.get(user=self.user2).chat, Chat.objects.all().get())
        # user1 back to the deleted chat
        ListOfChats.objects.create(user=self.user1, to_user=self.user2)
        self.assertEqual(ListOfChats.objects.count(), 2)
        self.assertEqual(Chat.objects.count(), 1)
        # delete all entries of Chat from ListOfChat
        chat1 = ListOfChats.objects.get(user=self.user1)
        chat1.delete()
        chat2 = ListOfChats.objects.get(user=self.user2)
        chat2.delete()
        self.assertEqual(ListOfChats.objects.count(), 0)
        self.assertEqual(Chat.objects.count(), 0)

    def test_chat_model_delete_method(self):
        """method Chat.delete() should delete self and all entries from ListOfChat"""
        chat = Chat.objects.all().get()
        chat.delete()
        self.assertEqual(ListOfChats.objects.count(), 0)
        self.assertEqual(Chat.objects.count(), 0)
