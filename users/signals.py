from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import OrganizerProfile, ParticipantProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    full_name = f"{instance.first_name} {instance.last_name}".strip()

    if created:
        if instance.user.role == "participant":
            ParticipantProfile.objects.create(user=instance)
        if instance.user.role == "organizer":
            OrganizerProfile.objects.create(user=instance)
    else:
        if instance.user.role == "participant":
            ParticipantProfile.objects.update_or_create(user=instance, defaults={"full_name": full_name})
        if instance.user.role == "organizer":
            OrganizerProfile.objects.update_or_create(user=instance, defaults={"full_name": full_name})
