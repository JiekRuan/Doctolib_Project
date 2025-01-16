import hashlib
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


# Modèle personnalisé pour l'utilisateur
class Account(AbstractUser):
    # On garde la relation ManyToMany avec groupes et permissions pour éviter les conflits
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    # Champ supplémentaire pour différencier les rôles
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    )
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default='patient'
    )

    def __str__(self):
        return f"{self.username} ({self.role})"


# Modèle pour le patient
class Patient(models.Model):
    # Numéro de sécurité sociale (PK)
    social_security_number = models.CharField(
        max_length=15, primary_key=True, unique=True
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    birth_date = models.DateField()
    email = models.EmailField(unique=True)
    postal_address = models.TextField()
    # Relation 1-1 avec le modèle utilisateur
    user = models.OneToOneField(
        Account, on_delete=models.CASCADE, related_name='patient'
    )

    def save(self, *args, **kwargs):
        # Hachage du numéro de sécurité sociale lors de la création
        if (
            not self.pk
        ):  # S'assure que le hachage est effectué uniquement à la création
            self.social_security_number = self.hash_social_security_number(
                self.social_security_number
            )
        super().save(*args, **kwargs)

    @staticmethod
    def hash_social_security_number(ssn):
        # Hachage avec SHA256
        return hashlib.sha256(ssn.encode('utf-8')).hexdigest()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# Modèle pour le médecin
class Doctor(models.Model):
    # Numéro RPPS (PK)
    rpps_number = models.CharField(
        max_length=11, primary_key=True, unique=True
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    specialty = models.CharField(max_length=100, default='Cardiologue')
    email = models.EmailField(unique=True)
    # Relation 1-1 avec le modèle utilisateur
    user = models.OneToOneField(
        Account, on_delete=models.CASCADE, related_name='doctor'
    )

    def save(self, *args, **kwargs):
        # Hachage du numéro RPPS lors de la création
        if not self.pk:
            self.rpps_number = self.hash_rpps_number(self.rpps_number)
        super().save(*args, **kwargs)

    @staticmethod
    def hash_rpps_number(rpps):
        # Hachage avec SHA256
        return hashlib.sha256(rpps.encode('utf-8')).hexdigest()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.specialty})"
