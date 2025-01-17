from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Account, Doctor, Patient


# Formulaire de connexion
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Nom d'utilisateur", max_length=255)
    password = forms.CharField(
        label="Mot de passe", widget=forms.PasswordInput
    )


# Formulaire d'inscription pour les patients
class PatientRegistrationForm(UserCreationForm):
    # Champs spécifiques au patient
    social_security_number = forms.CharField(
        label="Numéro de sécurité sociale", max_length=15
    )
    first_name = forms.CharField(label="Prénom", max_length=100)
    last_name = forms.CharField(label="Nom", max_length=100)
    phone_number = forms.CharField(label="Numéro de téléphone", max_length=15)
    birth_date = forms.DateField(
        label="Date de naissance",
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    postal_address = forms.CharField(
        label="Adresse postale", widget=forms.Textarea
    )

    class Meta:
        model = Account
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'patient'  # Définit le rôle comme patient
        if commit:
            user.save()

            # Créer l'objet Patient lié
            Patient.objects.create(
                user=user,
                social_security_number=self.cleaned_data[
                    'social_security_number'
                ],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                phone_number=self.cleaned_data['phone_number'],
                birth_date=self.cleaned_data['birth_date'],
                postal_address=self.cleaned_data['postal_address'],
                email=self.cleaned_data['email'],
            )
        return user


class DoctorRegistrationForm(UserCreationForm):
    
    SPECIALTY_CHOICES = [
        ('cardiologist', 'Cardiologue'),
        ('general_practitioner', 'Médecin généraliste'),
    ]
    rpps_number = forms.CharField(label="Numéro RPPS", max_length=11)
    first_name = forms.CharField(label="Prénom", max_length=50)
    last_name = forms.CharField(label="Nom", max_length=50)
    phone_number = forms.CharField(label="Numéro de téléphone", max_length=15)
    specialty = forms.ChoiceField(label="Spécialité", choices=[SPECIALTY_CHOICES])
    email = forms.EmailField(label="Adresse email")

    class Meta:
        model = Account
        fields = ['username', 'password1', 'password2', 'email']

    def clean_rpps_number(self):
        rpps_number = self.cleaned_data.get('rpps_number')
        if not rpps_number.isdigit() or len(rpps_number) != 11:
            raise forms.ValidationError(
                "Le numéro RPPS doit contenir exactement 11 chiffres."
            )
        return rpps_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'doctor'
        if commit:
            user.save()
            Doctor.objects.create(
                user=user,
                rpps_number=self.cleaned_data['rpps_number'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                phone_number=self.cleaned_data['phone_number'],
                specialty=self.cleaned_data['specialty'],
                email=self.cleaned_data['email'],
            )
        return user
