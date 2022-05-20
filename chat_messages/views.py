# django's libs
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic.edit import BaseUpdateView, BaseCreateView, DeletionMixin, BaseDetailView
from django.contrib.auth.mixins import UserPassesTestMixin
# other app's libs
from chats.views import ChatsView
from chats.models import Chat, ListOfChats
# this app's libs
from .models import Message
from .forms import MessageForm


class MessageView(ChatsView):
    template_name = 'by_bootstrap/message_list.html'
    context_object_name = 'messages_list'
    ordering = ['date']

    def test_func(self):
        inherited_test = ChatsView.test_func(self)
        if not inherited_test:
            return False
        # check the user is chat owner
        chat = get_object_or_404(Chat, id=self.kwargs['chat_id'])
        check_user_chat = self.request.user in chat.users_list()
        return check_user_chat

    def get_queryset(self):
        chat = get_object_or_404(Chat, id=self.kwargs['chat_id'])
        queryset = chat.message_set.all().order_by(*self.ordering)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get chats content
        context[ChatsView.context_object_name] = ChatsView.get_queryset(self)
        context['chat_id'] = self.kwargs['chat_id']
        # Message form context
        context['message_form'] = MessageForm()
        context['message_form_url'] = reverse(
            viewname='chats:new_message',
            kwargs={
                'user_id': self.kwargs['user_id'],
                'chat_id': self.kwargs['chat_id']
            }
        )
        return context

    def get_success_url(self):
        url = reverse(
            'chats:message_view',
            kwargs={
                'user_id': self.kwargs['user_id'],
                'chat_id': self.kwargs['chat_id'],
            })
        return url


class NewMessage(UserPassesTestMixin, BaseCreateView):
    form_class = MessageForm

    def test_func(self):
        return MessageView.test_func(self)

    def form_valid(self, form):
        # setup
        chat_id = self.kwargs["chat_id"]
        user_id = self.kwargs["user_id"]
        chat_list = ListOfChats.objects.get(user_id=user_id, chat_id=chat_id)
        chat = Chat.objects.get(id=chat_id)
        # set form instances
        form.instance.chat = chat
        form.instance.from_user = chat_list.user
        form.instance.to_user = chat_list.to_user
        return super().form_valid(form)

    def get_success_url(self):
        return MessageView.get_success_url(self)


class UpdateMessage(MessageView, BaseUpdateView):
    form_class = MessageForm
    pk_url_kwarg = 'message_id'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(self, request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Update message form for editing
        context['message_form'] = self.get_form()
        context['message_form_url'] = reverse(
            viewname='chats:update_message',
            kwargs={
                'user_id': self.kwargs['user_id'],
                'chat_id': self.kwargs['chat_id'],
                'message_id': self.kwargs['message_id'],
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('find_button'):
            super().post(request, args, kwargs)
            return HttpResponseRedirect(reverse(
                viewname='chats:update_message',
                kwargs={
                    'user_id': self.kwargs['user_id'],
                    'chat_id': self.kwargs['chat_id'],
                    'message_id': self.kwargs['message_id'],
            }))
        return BaseUpdateView.post(self, request, *args, **kwargs)

    def test_func(self):
        inherit_test = super().test_func()
        if not inherit_test:
            return False
        # check user in messages
        message = self.get_object()
        check_user_message = self.request.user == message.from_user
        return check_user_message


class DeleteMessage(UserPassesTestMixin, DeletionMixin, BaseDetailView):
    model = Message

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)

    def test_func(self):
        inherit_test = MessageView.test_func(self)
        if not inherit_test:
            return False
        # check user in message
        message = get_object_or_404(self.model, id=self.kwargs["pk"])
        # message = self.model.objects.get(id=self.kwargs["pk"])
        check_user_message = self.request.user == message.from_user
        return check_user_message

    def get_success_url(self):
        return MessageView.get_success_url(self)
