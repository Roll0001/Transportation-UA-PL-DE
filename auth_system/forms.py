from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Електронна пошта")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("username", None)
        self.fields.pop("first_name", None)
        self.fields.pop("last_name", None)

        self.fields["email"].widget.attrs.update({"placeholder": "example@mail.com"})
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Підтвердження пароля"
        self.fields["password1"].widget.attrs.update({"placeholder": "Введіть пароль"})
        self.fields["password2"].widget.attrs.update({"placeholder": "Повторіть пароль"})

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("Користувач з такою електронною поштою вже зареєстрований.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ("email", "password1", "password2")
        labels = {
            "email": "Електронна пошта",
            "password1": "Пароль",
            "password2": "Підтвердження пароля",
        }
        help_texts = {
            "email": "",
            "password1": "",
            "password2": "",
        }
