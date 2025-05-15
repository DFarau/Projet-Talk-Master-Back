import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    # Utilisation d'UUID comme clé primaire
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Champ email rendu explicite et requis (déjà dans AbstractUser mais on peut le redéfinir)
    email = models.EmailField(
        verbose_name='Adresse e-mail',
        max_length=255,
        unique=True,
    )
    
    role = models.CharField(
        max_length=20,
        choices=[
            ("organizer", "Organisateur"),
            ("speaker", "Conférencier"),
            ("public", "Participant"),
        ],
        default="public",
        verbose_name="Rôle",
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
  
    # Les talks organisés seront ajoutés après la définition du modèle Talk
    
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
    
    def __str__(self):
        return self.email if self.email else self.username


class Room(models.Model):
    """
    Modèle pour les salles de conférence
    """

    # Utilisation d'UUID comme clé primaire (optionnel)
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255, unique=True, verbose_name="Nom")

    class Meta:
        verbose_name = "Salle"
        verbose_name_plural = "Salles"

    def __str__(self):
        return self.name

class Talk(models.Model):
    """
    Modèle pour les présentations/conférences
    """

    LEVEL_CHOICES = [
        ("beginner", "Débutant"),
        ("intermediate", "Intermédiaire"),
        ("advanced", "Avancé"),
    ]

    STATUS_CHOICES = [
        ("pending", "En attente"),
        ("accepted", "Accepté"),
        ("rejected", "Refusé"),
    ]

    # Utilisation d'UUID comme clé primaire
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=255, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    start = models.DateTimeField(verbose_name="Heure de début")
    end = models.DateTimeField(verbose_name="Heure de fin")
    startdate = models.DateField(verbose_name="Jour")
    level = models.CharField(max_length=12, choices=LEVEL_CHOICES, verbose_name="Niveau")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="pending", verbose_name="Statut"
    )    # Relations
    speaker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="talks",
        limit_choices_to={
            "role": "speaker"
        },  # Limite le choix aux utilisateurs avec role='speaker'
        verbose_name="Conférencier",
    )
    speakerName = models.CharField(max_length=150, verbose_name="Nom du conférencier", blank=True)
    
    # Relation avec l'organisateur
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="organized_talks",
        limit_choices_to={
            "role": "organizer"
        },  # Limite le choix aux utilisateurs avec role='organizer'
        verbose_name="Organisateur",
        null=True,
        blank=True,
    )
    
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="talks",
        null=True,
        blank=True,
        verbose_name="Salle",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        verbose_name = "Présentation"
        verbose_name_plural = "Présentations"
        # Assure qu'un créneau dans une salle n'est pas doublement réservé
        constraints = [
            models.UniqueConstraint(
                fields=["room", "start", "end"],
                condition=models.Q(room__isnull=False),
                name="unique_room_time_slot",
            ),
        ]

    def __str__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        # Sauvegarde du nom du conférencier pour éviter des requêtes supplémentaires
        if self.speaker and not self.speakerName:
            self.speakerName = self.speaker.username
        super().save(*args, **kwargs)

    def clean(self):
        """Validation supplémentaire"""
        from django.core.exceptions import ValidationError

        # Vérifier que l'utilisateur est bien un conférencier
        if self.speaker and self.speaker.role != "speaker":
            raise ValidationError("Seul un conférencier peut être associé à un talk.")
            
        # Vérifier que la date de fin est après la date de début
        if self.start and self.end and self.start >= self.end:
            raise ValidationError("L'heure de fin doit être après l'heure de début.")
            
        # Vérifier que la date du jour correspond bien à la date des timestamps
        if self.start and self.startdate and self.start.date() != self.startdate:
            raise ValidationError("La date de début doit correspondre au jour indiqué.")
            
        # Vérifier qu'il n'y a pas de chevauchement pour ce conférencier
        if self.speaker and self.start and self.end:
            overlapping_talks = Talk.objects.filter(
                speaker=self.speaker,
                start__lt=self.end,
                end__gt=self.start
            ).exclude(pk=self.pk)

            if overlapping_talks.exists():
                raise ValidationError(
                    "Ce conférencier a déjà un talk programmé sur ce créneau horaire."
                )
