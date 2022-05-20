# django's libs
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.generic import ListView, RedirectView
from django.views.generic.edit import BaseCreateView, BaseDeleteView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
# other app's libs
from find_users.views import FindFormView
# this app's libs
from .models import ListOfChats
from .forms import AddChatForm


class HomePageRedirect(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        user_id = self.request.user.id
        url = reverse('chats:chats_list', kwargs={'user_id': user_id})
        return url


class ChatsView(UserPassesTestMixin, ListView):
    model = ListOfChats
    template_name = 'by_bootstrap/base_chats_list.html'
    context_object_name = 'chats_list'
    find_form = FindFormView()

    def test_func(self):
        return self.request.user.id == self.kwargs["user_id"]

    def get_queryset(self):
        user_id = self.request.user.id
        queryset = self.model.objects.filter(user=user_id)
        queryset = self.find_form.get_filtered_queryset(queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_id'] = self.kwargs['user_id']
        context['chat_id'] = None
        # set find form context
        context.update(self.find_form.get_context_data())
        return context

    def get(self, request, *args, **kwargs):
        self.find_form.get(request, args, kwargs)
        return super().get(request, args, kwargs)

    def post(self, request, *args, **kwargs):
        self.find_form.post(request, *args, **kwargs)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('chats:chats_list', kwargs={'user_id': self.kwargs['user_id']})


class NewChat(UserPassesTestMixin, BaseCreateView):
    form_class = AddChatForm

    def test_func(self):
        return ChatsView.test_func(self)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.to_user.id = self.request.POST['to_user']
        return super().form_valid(form)

    def form_invalid(self, form):
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        """redirect to the new chat messages"""
        url = reverse(
            'chats:message_view',
            kwargs={
                'user_id': self.kwargs['user_id'],
                'chat_id': self.object.chat.id
            })
        return url


class DeleteChat(UserPassesTestMixin, BaseDeleteView):
    model = ListOfChats

    def test_func(self):
        inherited_test = ChatsView.test_func(self)
        # check the user is chat owner
        chat_in_list = self.get_object()
        check_user_chat = self.request.user == chat_in_list.user
        return inherited_test and check_user_chat

    def get_success_url(self):
        return ChatsView.get_success_url(self)
