from django.shortcuts import render
from django.contrib.auth.decorators import login_required



# Create your views here.
def home(request):
    return render(request, 'Patient/home.html')
def patient_dashboard(request):
    return render(request, 'Patient/patient_dashboard.html')
