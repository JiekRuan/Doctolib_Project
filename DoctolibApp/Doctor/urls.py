from django.urls import path
from . import views

app_name = 'Doctor' 

urlpatterns = [
    path('', views.home, name='home'),  
    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
]
