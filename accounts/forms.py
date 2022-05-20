from django import forms
from django.contrib.auth import forms as forms_auth
from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _

# design classes for input elements in HTML page
DESIGN_CLASSES = "form-control"


class UserCreationForm (forms_auth.UserCreationForm):

    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "class": DESIGN_CLASSES,
            }
        ),
        help_text=password_validation.password_validators_help_text_html(),
    )

    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "class": DESIGN_CLASSES,
            }
        ),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta(forms_auth.UserCreationForm.Meta):
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": DESIGN_CLASSES,
                }
            ),
        }


class AuthenticationForm(forms_auth.AuthenticationForm):

    username = forms_auth.UsernameField(widget=forms.TextInput(
        attrs={
            "autofocus": True,
            "class": DESIGN_CLASSES,
        }
    ))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "class": DESIGN_CLASSES,
            }
        ),
    )


