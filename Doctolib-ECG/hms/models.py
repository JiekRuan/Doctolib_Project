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
    keras_model_path = models.CharField(max_length=255, default="modelV2Class_full.keras")

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
        """Traite le fichier CSV et stocke les prédictions dans la base de données."""
        if not self.csv_data:
            return None

        # Récupérer le chemin du fichier CSV
        csv_path = os.path.join(settings.MEDIA_ROOT, str(self.csv_data))

        # Vérifier que le fichier existe
        if not os.path.exists(csv_path):
            print(f"❌ Le fichier {csv_path} n'existe pas.")
            return None

        # Charger les données CSV dans un DataFrame Pandas
        try:
            df = pd.read_csv(csv_path, sep=';', header=None)
        except Exception as e:
            print(f"❌ Erreur lors de la lecture du CSV : {e}")
            return None

        # Vérifier la forme des données avant et après suppression de la dernière colonne
        print("Shape of the original dataframe:", df.shape)

        # Supprimer la dernière colonne si nécessaire (s'assurer qu'il reste bien 187 colonnes)
        df = df.iloc[:, :187]  # Garde les 187 premières colonnes

        print("Shape of the dataframe after removing the last column:", df.shape)

        # Convertir en numpy array
        X = df.values
        print("Shape of X before reshape:", X.shape)

        # Reshaper la donnée pour correspondre au format attendu par le modèle (1, 187, 1)
        X = X.reshape((1, 187, 1))
        print("Shape of X after reshape:", X.shape)

        # Charger le modèle Keras
        model_path = os.path.join(settings.MEDIA_ROOT, self.keras_model_path)

        if not os.path.exists(model_path):
            print(f"❌ Le modèle {model_path} n'existe pas.")
            return None

        try:
            model = tf.keras.models.load_model(model_path)
        except Exception as e:
            print(f"❌ Erreur lors du chargement du modèle : {e}")
            return None

        # Faire une prédiction avec le modèle
        predictions = model.predict(X)

        # Prendre la classe prédite (si le modèle fait une classification)
        predicted_classes = np.argmax(predictions, axis=1)

        print("Predicted class:", predicted_classes)

        # Dictionnaire des noms de classes
        # class_names = {
        #     0: "Battement normal (N)",
        #     1: "Contraction ventriculaire prématurée (PVC)",
        #     2: "Contraction auriculaire prématurée (PAC)",
        #     3: "Battement de fusion (FB)",
        #     4: "Battement non classifiable (U)"
        # }
        class_names ={
            1: "Battement normal",
            2: "Battement normal"

        }
        # Remplacer les indices des classes par leurs noms
        predictions_with_names = [class_names[class_num] for class_num in predicted_classes]

        # Convertir les prédictions en format JSON pour les enregistrer dans la base de données
        predictions_json = json.dumps(predictions_with_names)

        # Sauvegarder les prédictions dans la base de données
        self.predictions = predictions_json
        self.save()

        # Retourner les prédictions avec les noms
        return predictions_with_names

