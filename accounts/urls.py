"""accounts URL Configuration"""
from django.urls import path, include
from .views import SignupView

app_name = 'accounts'
urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('signup/', SignupView.as_view(), name='signup'),
]
