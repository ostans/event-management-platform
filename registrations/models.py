from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseModel
from events.models import Event, Stage


class Registration(BaseModel):

    class Status(models.TextChoices):
        REGISTERED = "registered", "Registered"
        CANCELLED = "cancelled", "Cancelled"

    participant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="registrations")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations")
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, null=True, blank=True, related_name="registrations")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.REGISTERED)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["event", "participant"],
                condition=models.Q(stage__isnull=True),
                name="uq_registration_event_scope",
            ),
            models.UniqueConstraint(
                fields=["event", "participant", "stage"],
                condition=models.Q(stage__isnull=False),
                name="uq_registration_stage_scope",
            ),
        ]

    def __str__(self):
        return f"{self.participant} - {self.event}"

    def clean(self):
        errors = {}
        if self.event.registration_scope == Event.RegistrationScope.STAGE and not self.stage:
            errors["stage"] = ValidationError(f"Stage is required for event {self.event}")
        elif self.event.registration_scope == Event.RegistrationScope.EVENT and self.stage:
            errors["stage"] = ValidationError(f"Stage is not required for event {self.event}")

        if self.stage and self.stage.event != self.event:
            errors["stage"] = ValidationError(f"Stage {self.stage} does not belong to event {self.event}")

        if errors:
            raise ValidationError(errors)
