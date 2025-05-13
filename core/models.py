import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone





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


class TimeSlot(models.Model):
    """
    Modèle pour les créneaux horaires
    """

    # Utilisation d'UUID comme clé primaire (optionnel)
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    start = models.DateTimeField(verbose_name="Début")
    end = models.DateTimeField(verbose_name="Fin")

    class Meta:
        verbose_name = "Créneau horaire"
        verbose_name_plural = "Créneaux horaires"
        constraints = [
            # Assure que la fin est après le début
            models.CheckConstraint(
                check=models.Q(end__gt=models.F("start")), name="check_end_greater_than_start"
            ),
        ]

    def __str__(self):
        return f"{self.start.strftime('%d/%m/%Y %H:%M')} - {self.end.strftime('%H:%M')}"

    def clean(self):
        """Validation supplémentaire"""
        from django.core.exceptions import ValidationError

        if self.start and self.end and self.start >= self.end:
            raise ValidationError("La fin du créneau doit être après le début.")


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
        ("scheduled", "Planifié"),
    ]

    # Utilisation d'UUID comme clé primaire (optionnel)
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    title = models.CharField(max_length=255, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    duration = models.IntegerField(verbose_name="Durée (en minutes)")
    level = models.CharField(max_length=12, choices=LEVEL_CHOICES, verbose_name="Niveau")
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="pending", verbose_name="Statut"
    )

    # Relations
    speaker = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="talks",
        limit_choices_to={
            "role": "speaker"
        },  # Limite le choix aux utilisateurs avec role='speaker'
        verbose_name="Conférencier",
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="talks",
        null=True,
        blank=True,  # Optionnel tant que le talk n'est pas planifié
        verbose_name="Salle",
    )
    timeslot = models.ForeignKey(
        TimeSlot,
        on_delete=models.CASCADE,
        related_name="talks",
        null=True,
        blank=True,  # Optionnel tant que le talk n'est pas planifié
        verbose_name="Créneau horaire",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")

    class Meta:
        verbose_name = "Présentation"
        verbose_name_plural = "Présentations"
        # Assure qu'un conférencier ne peut pas avoir deux talks qui se chevauchent
        constraints = [
            models.UniqueConstraint(
                fields=["room", "timeslot"],
                condition=models.Q(room__isnull=False, timeslot__isnull=False),
                name="unique_room_timeslot",
            ),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        """Validation supplémentaire"""
        from django.core.exceptions import ValidationError

        # Vérifier que l'utilisateur est bien un conférencier
        if self.speaker and self.speaker.role != "speaker":
            raise ValidationError("Seul un conférencier peut être associé à un talk.")

        # Vérifier que room et timeslot sont tous les deux définis si le statut est 'scheduled'
        if self.status == "scheduled":
            if not self.room:
                raise ValidationError("Une salle doit être attribuée pour planifier un talk.")
            if not self.timeslot:
                raise ValidationError(
                    "Un créneau horaire doit être attribué pour planifier un talk."
                )

        # Vérifier qu'il n'y a pas de chevauchement pour ce conférencier
        if self.speaker and self.timeslot:
            overlapping_talks = Talk.objects.filter(
                speaker=self.speaker, timeslot=self.timeslot
            ).exclude(pk=self.pk)

            if overlapping_talks.exists():
                raise ValidationError(
                    "Ce conférencier a déjà un talk programmé sur ce créneau horaire."
                )


class Favorite(models.Model):
    """
    Modèle pour les talks favoris des utilisateurs
    """

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="favorites", verbose_name="Utilisateur"
    )
    talk = models.ForeignKey(
        Talk, on_delete=models.CASCADE, related_name="favorited_by", verbose_name="Présentation"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")

    class Meta:
        verbose_name = "Favori"
        verbose_name_plural = "Favoris"
        # Un utilisateur ne peut ajouter un talk en favori qu'une seule fois
        unique_together = ["user", "talk"]

    def __str__(self):
        return f"{self.user.email} - {self.talk.title}"
