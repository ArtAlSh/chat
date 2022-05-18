from django import forms


class FindForm(forms.Form):
    find_field = forms.CharField(max_length=20, required=False)

