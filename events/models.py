from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from accounts.models import phone_regex
from core.models import BaseModel


class EventType(models.Model):
    """Categorizes events (tournament, webinar, workshop, sports, ...)
    and optionally scopes which dynamic Attributes apply to it."""

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=250)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Event(BaseModel):

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        CLOSED = "closed", "Closed"
        FINISHED = "finished", "Finished"

    # Legal status transitions, per the assignment spec.
    ALLOWED_TRANSITIONS = {
        Status.DRAFT: {Status.PUBLISHED},
        Status.PUBLISHED: {Status.DRAFT, Status.CLOSED},
        Status.CLOSED: {Status.PUBLISHED, Status.FINISHED},
        Status.FINISHED: set(),
    }

    class RegistrationScope(models.TextChoices):
        EVENT = "event", "Whole event"
        STAGE = "stage", "Per stage"

    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="organized_events")
    event_type = models.ForeignKey(EventType, on_delete=models.SET_NULL, null=True, blank=True, related_name="events")
    title = models.CharField(max_length=250)
    description = models.TextField(null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    registration_scope = models.CharField(
        max_length=10, choices=RegistrationScope.choices, default=RegistrationScope.EVENT
    )
    capacity = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def clean(self):
        if self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")

        if self.registration_scope == self.RegistrationScope.EVENT and self.capacity is None:
            raise ValidationError("Capacity is required for event-level registration.")
        elif self.registration_scope == self.RegistrationScope.STAGE and self.capacity is not None:
            raise ValidationError("Capacity is not allowed for stage-level registration.")

        if self.pk:
            previous_status = Event.objects.filter(pk=self.pk).values_list("status", flat=True).first()
            if previous_status and previous_status != self.status:
                allowed = self.ALLOWED_TRANSITIONS.get(previous_status, set())
                if self.status not in allowed:
                    raise ValidationError(f"Cannot change status from {previous_status} to {self.status}.")


class Stage(BaseModel):

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="stages")
    title = models.CharField(max_length=250)
    description = models.TextField(null=True, blank=True)
    order_index = models.PositiveIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.PositiveIntegerField(null=True, blank=True)

    def clean(self):
        if self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")

        if self.event.registration_scope == Event.RegistrationScope.STAGE and self.capacity is None:
            raise ValidationError("Capacity is required for stage-level registration.")
        elif self.event.registration_scope == Event.RegistrationScope.EVENT and self.capacity is not None:
            raise ValidationError("Capacity is not allowed for event-level registration.")

    class Meta:
        unique_together = ("event", "order_index")


class StageRoleType(models.Model):

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=250)

    class Meta:
        verbose_name = "Stage Role"
        verbose_name_plural = "Stage Roles"
        ordering = ["name"]

    def __str__(self):
        return self.name


class StageAssignment(BaseModel):

    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="assignments")
    guest_name = models.CharField(max_length=250)
    guest_phone_number = models.CharField(max_length=13, validators=[phone_regex])
    role_type = models.ForeignKey(StageRoleType, on_delete=models.PROTECT, related_name="assignments")

    class Meta:
        ordering = ["stage", "role_type"]
        unique_together = ("stage", "guest_phone_number", "role_type")

    def __str__(self):
        return f"{self.guest_name} - {self.role_type } @ {self.stage}"
