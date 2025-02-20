from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from hms.user_manager import UserManager
from hms.base_model import BaseModel
import numpy as np

# Create your models here.
import os
import json
import pandas as pd
import tensorflow as tf
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property
from django.core.validators import validate_email
import joblib
from sklearn.preprocessing import StandardScaler


class User(BaseModel, AbstractUser):
    USER_TYPE = (
        ("Patient", "Patient"),
        ("Doctor", "Doctor"),
    )

    email = models.EmailField(_('email address'), blank=False, unique=True)
    phone_number = models.CharField(max_length=13, blank=True, null=True)
    doctor = models.ForeignKey("self", null=True, blank=True,
                               related_name="patients", on_delete=models.SET_NULL)
    role = models.CharField(max_length=10, choices=USER_TYPE)

    # 🔹 Champ pour stocker le fichier CSV
    csv_data = models.FileField(upload_to='csv_uploads/', blank=True, null=True)
    csv_upload_date = models.DateTimeField(null=True, blank=True)

    # 🔹 Champ pour stocker le chemin du modèle Keras (si besoin de plusieurs modèles)
    keras_model_path = models.CharField(max_length=255, default="./modelV2Class_full.keras")
    # 🔹 Stockage des prédictions en JSON
    predictions = models.JSONField(null=True, blank=True)

    # 🔹 Suppression de `username` et utilisation de l'email comme identifiant
    
    username = None
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    @cached_property
    def full_name(self):
        return self.get_full_name()

    def save(self, *args, **kwargs):
        """ Validation de l'email avant de sauvegarder l'utilisateur """
        if not self.email:
            raise ValidationError(_("Email address cannot be empty"))

        try:
            validate_email(self.email)
        except ValidationError as e:
            raise ValidationError(str(e))

        super(User, self).save(*args, **kwargs)


    def process_csv_with_keras(self):
        """Traite le fichier CSV, effectue des prédictions et retourne la classe prédite."""
        if not self.csv_data:
            return None

        # Récupérer le chemin du fichier CSV
        csv_path = os.path.join(settings.MEDIA_ROOT, str(self.csv_data))
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Le fichier CSV {csv_path} n'existe pas.")

        # Charger les données CSV
        try:
            df = pd.read_csv(csv_path, sep=";", header=None)
        except Exception as e:
            raise ValueError(f"Erreur lors de la lecture du fichier CSV : {e}")

        # Convertir en numpy array
        X = df.values

        # Charger le scaler
        scaler_path = os.path.join(settings.MEDIA_ROOT, "./scaler.pkl")
        scaler = joblib.load(scaler_path)
        X_scaled = scaler.transform(X)
        X_scaled = X_scaled.reshape((X_scaled.shape[0], X_scaled.shape[1], 1))

        # Charger le modèle Keras
        model_path = os.path.join(settings.MEDIA_ROOT, self.keras_model_path)
        print(model_path)
        model = tf.keras.models.load_model(model_path)
        print(model.summary())

        # Faire une prédiction
        predictions = model.predict(X_scaled)

        # Obtenir la classe prédite
        predicted_classes = np.argmax(predictions, axis=1)

        # Mapping des classes
        class_names = {
            0: "Battement normal (N)",
            1: "Contraction ventriculaire prématurée (PVC)",
            2: "Contraction auriculaire prématurée (PAC)",
            3: "Battement de fusion (FB)",
            4: "Battement non classifiable (U)"
        }
        predicted_class_labels = [class_names[cls] for cls in predicted_classes]

        # Sauvegarder la classe prédite
        predictions_json = json.dumps(predicted_class_labels)
        self.predictions = predictions_json
        self.save()

        # Retourner uniquement la classe prédite sous forme de noms
        return predicted_class_labels   
