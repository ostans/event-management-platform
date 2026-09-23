from django.core.exceptions import FieldDoesNotExist
from django.test import TestCase

from .admin import FeedbackAdmin
from .models import Feedback


class FeedbackFieldRegressionTests(TestCase):
    def test_feedback_has_registration_foreign_key(self):
        self.assertIsNotNone(Feedback._meta.get_field("registration"))

    def test_feedback_admin_uses_registration_relation(self):
        self.assertIn("registration__event", FeedbackAdmin.list_display)
