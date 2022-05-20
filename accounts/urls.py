"""accounts URL Configuration"""
from django.urls import path, include
from .views import SignupView, LoginView

app_name = 'accounts'
urlpatterns = [
    path('login/', LoginView.as_view(), name="login"),
    path('signup/', SignupView.as_view(), name='signup'),
    path('', include('django.contrib.auth.urls')),
]
