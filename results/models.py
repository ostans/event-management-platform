from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from core.models import BaseModel
from events.models import Event, Stage
from registrations.models import Registration


class Result(BaseModel):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="results")
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, null=True, blank=True, related_name="results")
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="results"
    )
    rank = models.PositiveIntegerField(null=True, blank=True)
    score = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    label = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ["event", "stage", "rank"]
        verbose_name_plural = "Results"
        constraints = [
            models.UniqueConstraint(
                fields=["event", "participant"],
                condition=models.Q(stage__isnull=True, participant__isnull=False),
                name="uq_result_event_participant",
            ),
            models.UniqueConstraint(
                fields=["event", "stage", "participant"],
                condition=models.Q(stage__isnull=False, participant__isnull=False),
                name="uq_result_stage_participant",
            ),
            models.CheckConstraint(
                condition=models.Q(rank__isnull=False) | models.Q(score__isnull=False),
                name="result_rank_or_score_required",
            ),
            models.CheckConstraint(
                condition=models.Q(rank__isnull=True) | models.Q(rank__gte=1),
                name="result_rank_positive",
            ),
        ]

    def __str__(self):
        parts = []
        if self.rank is not None:
            parts.append(f"rank={self.rank}")
        if self.score is not None:
            parts.append(f"score={self.score}")
        summary = ", ".join(parts)
        return f"{self.participant} - {self.event} - {self.stage}: {summary}"

    def clean(self):
        errors = {}

        if self.rank is None and self.score is None:
            errors["__all__"] = "Result must have either a rank or a score"

        if self.stage_id and self.stage.event_id != self.event_id:
            errors["stage"] = f"The stage must belong to the event {self.event}."

        if self.is_published and self.event.status != Event.Status.FINISHED:
            errors["is_published"] = "Results can only be published for finished events."

        if self.participant_id:
            has_registration = Registration.objects.filter(
                event=self.event,
                participant_id=self.participant_id,
                status=Registration.Status.REGISTERED,
                **({"stage": self.stage} if self.stage_id else {}),
            ).exists()
            if not has_registration:
                errors["participant"] = f"'{self.participant}' is not registered for this event."

        if errors:
            raise ValidationError(errors)


class Feedback(BaseModel):
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name="feedback")
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(verbose_name="Feedback", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rating__gte=1) & models.Q(rating__lte=5),
                name="feedback_rating_between_1_and_5",
            ),
        ]

    def __str__(self):
        return f"{self.registration.participant.name} - {self.rating} {f"{self.comment[:20]}" if self.comment else ""}"

    def clean(self):
        errors = {}

        if not (1 <= self.rating <= 5):
            errors["rating"] = "Rating must be between 1 and 5."

        if self.registration_id and self.registration.event.status != Event.Status.FINISHED:
            errors["registration"] = "Event must be finished to give feedback."

        if errors:
            raise ValidationError(errors)
