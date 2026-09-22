from django.test import TestCase

from accounts.models import User
from users.models import OrganizerProfile, ParticipantProfile


class UserProfileSignalTests(TestCase):
    def test_participant_profile_created_for_new_user(self):
        user = User.objects.create_user(
            phone_number="+989000000001",
            password="secretpass",
            first_name="Test",
            last_name="User",
            role="participant",
        )

        self.assertTrue(ParticipantProfile.objects.filter(user=user).exists())
        self.assertFalse(OrganizerProfile.objects.filter(user=user).exists())

    def test_organizer_profile_created_for_new_user(self):
        user = User.objects.create_user(
            phone_number="+989000000002",
            password="secretpass",
            first_name="Org",
            last_name="Admin",
            role="organizer",
        )

        self.assertTrue(OrganizerProfile.objects.filter(user=user).exists())
        self.assertFalse(ParticipantProfile.objects.filter(user=user).exists())
