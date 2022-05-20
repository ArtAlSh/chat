from django import forms


class CharFieldWithAttrs(forms.CharField):

    def __init__(self, max_length=None, min_length=None, strip=True, empty_value="", attrs=None, *args, **kwargs):
        self.attrs = attrs
        super().__init__(
            max_length=max_length, min_length=min_length, strip=strip, empty_value=empty_value,  *args, **kwargs
        )

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        attrs.update(self.attrs)
        return attrs


class FindForm(forms.Form):
    find_field = CharFieldWithAttrs(
        max_length=20, required=False,
        attrs={
            "class": "form-control",
            "placeholder": "find user",
        }
    )


