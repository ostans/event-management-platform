from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.conf import settings
from django.db import models
from django_resized import ResizedImageField

from core.models import BaseModel


class ParticipantProfile(BaseModel):
    """ParticipantProfile
        This is the model for the participant profile
    Arguments:
        BaseModel {_type_} -- it inherits from BaseModel
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="participant_profile")
    full_name = models.CharField(max_length=300)
    avatar = ResizedImageField(size=[256, 256], quality=75, upload_to="participant_avatars/", null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    events_attended = models.PositiveIntegerField(default=0, editable=True)
    history = AuditlogHistoryField()

    class Meta:
        verbose_name = "Participant Profile"
        verbose_name_plural = "Participant Profiles"
        ordering = ["-created_at"]

    def __str__(self):
        return self.full_name


auditlog.register(ParticipantProfile)


class OrganizerProfile(BaseModel):
    """OrganizerProfile
        This model is used to store the organizer profile

    Arguments:
        BaseModel {_type_} -- it inherits from BaseModel
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="organizer_profile")
    full_name = models.CharField(max_length=300)
    organization_name = models.CharField(max_length=100)
    logo = ResizedImageField(size=[256, 256], quality=75, upload_to="organizer_logos/", null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    events_organized = models.PositiveIntegerField(default=0, editable=True)
    history = AuditlogHistoryField()

    class Meta:
        verbose_name = "Organizer Profile"
        verbose_name_plural = "Organizer Profiles"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.organization_name}"


auditlog.register(OrganizerProfile)
