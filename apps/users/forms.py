from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# class joinForm(forms.ModelForm):
#     class Meta:
#         model = users
#         fields = ['username', 'password']

class joinForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']