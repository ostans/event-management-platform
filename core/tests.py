from django.conf import settings
from django.test import SimpleTestCase


class SettingsCompatibilityTest(SimpleTestCase):
    def test_nplusone_django_integration_is_registered(self):
        self.assertIn("nplusone.ext.django", settings.INSTALLED_APPS)
        self.assertIn("nplusone.ext.django.NPlusOneMiddleware", settings.MIDDLEWARE)
