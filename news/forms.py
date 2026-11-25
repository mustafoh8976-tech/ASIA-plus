from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Comment, CustomUser


class RegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = ("username", "email")


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Напишите комментарий",
                }
            )
        }
