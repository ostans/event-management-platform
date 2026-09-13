from auditlog.models import LogEntry
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import *
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from core.permissions import IsOwner, IsStaffUser

from .models import OrganizerProfile, ParticipantProfile
from .serializers import (
    LogEntrySerializer,
    OrganizerProfileSerializer,
    ParticipantProfileSerializer,
)


@method_decorator(cache_page(60 * 15), name="dispatch")
class BaseProfileViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwner, IsStaffUser]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_staff:
            return qs
        return qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ParticipantProfileViewSet(BaseProfileViewSet):
    queryset = ParticipantProfile.objects.all()
    serializer_class = ParticipantProfileSerializer


class OrganizerProfileViewSet(BaseProfileViewSet):
    queryset = OrganizerProfile.objects.all()
    serializer_class = OrganizerProfileSerializer


class LogEntryViewSet(ReadOnlyModelViewSet):
    """
    Read-only access to audit log entries. Staff-only by default.
    """

    queryset = LogEntry.objects.all().select_related("content_type", "actor")
    serializer_class = LogEntrySerializer
    permission_classes = [IsStaffUser]
