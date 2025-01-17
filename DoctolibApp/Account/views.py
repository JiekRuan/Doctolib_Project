from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, DoctorRegistrationForm, PatientRegistrationForm


# Page d'accueil
def home(request):
    return render(request, 'Account/home.html')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirection basée sur le rôle
                if user.role == 'doctor':
                    return redirect('doctor_dashboard')
                elif user.role == 'patient':
                    return redirect('patient_dashboard')
    else:
        form = LoginForm()
    return render(request, 'Account/login.html', {'form': form})


# Page de déconnexion
def logout_view(request):
    logout(request)
    return redirect('login')


def register_doctor(request):
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('Doctor:doctor_dashboard')
    else:
        form = DoctorRegistrationForm()
    return render(request, 'Account/register_doctor.html', {'form': form})


# Inscription pour les patients
def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(
                'Patient:patient_dashboard'
            )  
    else:
        form = PatientRegistrationForm()
    return render(request, 'Account/register_patient.html', {'form': form})



def patient_dashboard(request):
    return render(request, 'Patient/patient_dashboard.html')


@login_required
def doctor_dashboard(request):
    return render(request, 'Doctor/doctor_dashboard.html')
