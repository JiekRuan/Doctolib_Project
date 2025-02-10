from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.views import generic
from hms.models import User
from hms.forms import LoginForm, CSVUploadForm
import json
# Create your views here.

class HomeView(generic.TemplateView):
    template_name = 'home.html'


def signup(request):
    doctors = User.objects.filter(role="Doctor")
    user = request.user
    if user.is_authenticated:
        return redirect('dashboard')
    
    default_role = request.GET.get('role')
    
    context = {
        'doctors': doctors,
        'default_role': default_role
    }
    
    if request.method == 'POST':
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone_number = request.POST['phone']
        role = request.POST['role']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        doctor_id = request.POST.get('doctor')

        print("DOCTOR ID", doctor_id)

        if password != confirm_password:
            messages.error(request, "Mot de passe ne corresponds pas")
            return redirect('signup')

        if role == 'Patient' and not doctor_id:
            messages.error(request, "Un patient doit selectionner un docteur")
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email déjà existant.")
            return redirect('signup')

        user = User.objects.create_user(email=email, password=password, phone_number=phone_number, doctor_id=doctor_id, role=role, first_name=first_name, last_name=last_name)
        user.save()
        return redirect("login")
    return render(request, 'signup.html', context)


class LoginView(generic.FormView):
    form_class = LoginForm
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            if self.request.user.role == "Patient":
                return redirect('patient_detail', pk=self.request.user.pk)
            return redirect('doctor_detail', pk=self.request.user.pk)
        else:
            return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        user = authenticate(email=email, password=password)
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        messages.error(self.request, "Mot de passe incorrect")
        return super().form_invalid(form)

    def get_success_url(self) -> str:
        user = self.request.user
        if user.is_authenticated:
            if user.role == "Patient":
                return reverse('patient_detail', kwargs={"pk": user.pk})
            else:
                return reverse("doctor_detail",  kwargs={"pk": user.pk})
        return reverse('login')
    

class DoctorDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'doctor_detail.html'
    context_object_name = 'doctor'

    def get_object(self, queryset=None):
        doctor = get_object_or_404(User, id=self.kwargs['pk'], role='Doctor')
        return doctor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patients'] = self.object.patients.all()
        return context





# class PatientDetailView(LoginRequiredMixin, DetailView):
#      model = User
#      template_name = 'patient_detail.html'
#      context_object_name = 'patient'

#      def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['csv_form'] = CSVUploadForm()
#         context['success_message'] = None  # Initialiser la variable message
#         context['error_message'] = None    # Initialiser l'éventuel message d'erreur

#         # Si des prédictions existent et que l'upload a été effectué
#         if self.request.method == 'POST':
#             form = CSVUploadForm(self.request.POST, self.request.FILES)
#             if form.is_valid():
#                 self.object = self.get_object()  # On récupère l'objet patient
#                 self.object.csv_data = form.cleaned_data['csv_file']
#                 self.object.csv_upload_date = timezone.now()
#                 self.object.save()

#                 # 🔥 Traitement du fichier CSV avec Keras
#                 predictions = self.object.process_csv_with_keras()

#                 if predictions is not None:
#                     context['success_message'] = f'CSV téléchargé ! Votre ECG est de classe: {predictions[0]}'
#                 else:
#                     context['error_message'] = 'Le modèle ne fonctionne pas pour ce fichier.'

#             else:
#                 context['error_message'] = 'Le fichier CSV n\'est pas valide.'

#         return context


#      def post(self, request, *args, **kwargs):
#         # Traitement de POST est déjà géré dans get_context_data, donc pas besoin de redondance ici
#         return self.get(request, *args, **kwargs)

#      def get_object(self, queryset=None):
#          patient = get_object_or_404(User, id=self.kwargs['pk'], role='Patient')

#          if self.request.user != patient and self.request.user != patient.doctor:
#              raise PermissionDenied
            
#          return patient
    
    # def process_csv_with_transformer_mode(self, csv_file):
    #     object = self.get_object()
    #     # Generate data from model and save to csv_model_data field
    #     csv_model_data = None
    #     object.csv_model_data = csv_model_data
    #     object.save()
    #     return csv_model_data

class PatientDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'patient_detail.html'
    context_object_name = 'patient'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['csv_form'] = CSVUploadForm()
        context['success_message'] = None  # Initialiser la variable message
        context['error_message'] = None    # Initialiser l'éventuel message d'erreur

        # Si des prédictions existent et que l'upload a été effectué
        if self.request.method == 'POST':
            form = CSVUploadForm(self.request.POST, self.request.FILES)
            if form.is_valid():
                self.object = self.get_object()  # On récupère l'objet patient
                self.object.csv_data = form.cleaned_data['csv_file']
                self.object.csv_upload_date = timezone.now()
                self.object.save()

                # 🔥 Traitement du fichier CSV avec Keras
                predictions = self.object.process_csv_with_keras()

            #     if predictions is not None:
            #         context['success_message'] = f'CSV téléchargé ! Votre ECG est de classe: {predictions[0]}'
            #     else:
            #         context['error_message'] = 'Le modèle ne fonctionne pas pour ce fichier.'
            # else:
            #     context['error_message'] = 'Le fichier CSV n\'est pas valide.'

        # Ajouter les prédictions du patient au contexte
        if self.object.predictions:
            context['predictions'] = json.loads(self.object.predictions)  # Charger les prédictions en JSON

        return context

    def post(self, request, *args, **kwargs):
        # Traitement de POST est déjà géré dans get_context_data, donc pas besoin de redondance ici
        return self.get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        patient = get_object_or_404(User, id=self.kwargs['pk'], role='Patient')

        if self.request.user != patient and self.request.user != patient.doctor:
            raise PermissionDenied
            
        return patient

            

    
