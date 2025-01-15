from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
from .forms import MedecinRegistrationForm
from .forms import PatientRegistrationForm

def home(request):
    return render(request, 'Account/home.html') 

# Page de connexion
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Redirige vers la page d'accueil ou autre page après connexion
    else:
        form = AuthenticationForm()
    return render(request, 'Account/login.html', {'form': form})

def register_medecin(request):
    if request.method == 'POST':
        form = MedecinRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = MedecinRegistrationForm()
    return render(request, 'register_medecin.html', {'form': form})

def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = PatientRegistrationForm()
    return render(request, 'register_patient.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    if request.user.role == 'medecin':
        return render(request, 'medecin_dashboard.html')
    elif request.user.role == 'patient':
        return render(request, 'patient_dashboard.html')
    else:
        return redirect('login')



