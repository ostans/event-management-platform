from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import OrganizerProfile, ParticipantProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    full_name = f"{instance.first_name} {instance.last_name}".strip()

    if created:
        if instance.role == "participant":
            ParticipantProfile.objects.create(user=instance, full_name=full_name)
        elif instance.role == "organizer":
            OrganizerProfile.objects.create(user=instance, full_name=full_name)
    else:
        if instance.role == "participant":
            ParticipantProfile.objects.update_or_create(user=instance, defaults={"full_name": full_name})
        elif instance.role == "organizer":
            OrganizerProfile.objects.update_or_create(user=instance, defaults={"full_name": full_name})
