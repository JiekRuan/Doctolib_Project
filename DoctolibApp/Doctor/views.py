from django.shortcuts import render

# Create your views here.


def home(request):
    return render(request, 'Doctor/home.html')


def doctor_dashboard(request):
    return render(request, 'Doctor/doctor_dashboard.html')
