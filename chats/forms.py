from django import forms
from .models import ListOfChats


class AddChatForm(forms.ModelForm):
    class Meta:
        model = ListOfChats
        fields = {'to_user': 'user2'}
        widgets = {
            'to_user': forms.HiddenInput(),
        }
