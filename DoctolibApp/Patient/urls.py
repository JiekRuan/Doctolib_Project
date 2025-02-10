from django.urls import path
from . import views

app_name = 'Patient'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
]
