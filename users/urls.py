from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    LogEntryViewSet,
    OrganizerProfileViewSet,
    ParticipantProfileViewSet,
)

router = DefaultRouter()
router.register(r"participant-profiles", ParticipantProfileViewSet, basename="participant-profile")
router.register(r"organizer-profiles", OrganizerProfileViewSet, basename="organizer-profile")
router.register(r"audit-logs", LogEntryViewSet, basename="audit-log")

urlpatterns = [
    path("", include(router.urls)),
]
