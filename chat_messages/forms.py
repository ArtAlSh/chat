from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']
        labels = {'text': "Your message"}
        widgets = {
            'text': forms.Textarea(
                attrs={
                    "placeholder": "Message",
                    "class": "form-control rounded-2",
                    "style": "resize: none; height: 50px;",
                })
        }
