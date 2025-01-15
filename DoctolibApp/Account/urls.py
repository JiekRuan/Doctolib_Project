from django.urls import path
from . import views

app_name = 'account'  # Ajoute un espace de nom pour éviter les conflits

urlpatterns = [
    path('register/medecin/', views.register_medecin, name='register_medecin'),
    path('register/patient/', views.register_patient, name='register_patient'),
    path('', views.home, name='home'),  # Page d'accueil pour l'application Account
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
