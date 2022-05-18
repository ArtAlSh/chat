from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['text']
        labels = {'text': "Your message"}
        widgets = {
            'text': forms.Textarea(attrs={"cols": "20", "rows": "1", "placeholder": "Message"})
        }