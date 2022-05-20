from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView
from django.contrib.auth import views
from .forms import UserCreationForm, AuthenticationForm


class SignupView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('chats:home')


class LoginView(views.LoginView):
    form_class = AuthenticationForm
