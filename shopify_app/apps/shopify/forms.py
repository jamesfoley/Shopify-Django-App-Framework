from django import forms


class Login(forms.Form):
    shop = forms.CharField()