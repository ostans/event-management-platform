from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User


class LogoutApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone_number="+989000000010",
            password="secretpass",
            first_name="Alice",
            last_name="Example",
            role="participant",
        )
        self.client = APIClient()

    def test_logout_rejects_refresh_token_for_other_user(self):
        other_user = User.objects.create_user(
            phone_number="+989000000011",
            password="secretpass",
            first_name="Bob",
            last_name="Example",
            role="participant",
        )

        access_token = (
            __import__("rest_framework_simplejwt.tokens", fromlist=["RefreshToken"])
            .RefreshToken.for_user(self.user)
            .access_token
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        other_refresh_token = __import__(
            "rest_framework_simplejwt.tokens", fromlist=["RefreshToken"]
        ).RefreshToken.for_user(other_user)
        response = self.client.post(reverse("logout"), {"refresh": str(other_refresh_token)}, format="json")

        self.assertEqual(response.status_code, 403)
