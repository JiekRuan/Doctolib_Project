from django import forms
from .models import Account
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Nom d'utilisateur", max_length=255)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)


class MedecinRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ['username', 'password']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'medecin'
        if commit:
            user.save()
        return user

class PatientRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = ['username', 'password']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'patient'
        if commit:
            user.save()
        return user
