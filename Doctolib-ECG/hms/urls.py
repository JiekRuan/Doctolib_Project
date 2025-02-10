from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

from . import views


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path("login/", views.LoginView.as_view(template_name="login.html"), name="login"),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path("signup/", views.signup, name="signup"),
    path('doctor/<int:pk>/', views.DoctorDetailView.as_view(), name='doctor_detail'),
    path('patient/<int:pk>/', views.PatientDetailView.as_view(), name='patient_detail'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
