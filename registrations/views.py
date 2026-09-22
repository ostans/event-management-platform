from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import IsEventOwner, IsOrganizer, IsParticipant
from events.models import Event

from .models import Registration
from .serializers import (
    RegistrationCancelSerializer,
    RegistrationCreateSerializer,
    RegistrationOrganizerSerializer,
    RegistrationSerializer,
)


# ---------------------------------------------------------------------
# Participant — own registrations
# GET/POST /registrations/
# GET      /registrations/{pk}/
# POST     /registrations/{pk}/cancel/
# ---------------------------------------------------------------------
class RegistrationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = [permissions.IsAuthenticated, IsParticipant]
    lookup_value_regex = r"[0-9]+"

    def get_queryset(self):
        return Registration.objects.filter(participant=self.request.user).select_related("event", "stage")

    def get_serializer_class(self):
        if self.action == "create":
            return RegistrationCreateSerializer
        if self.action == "cancel":
            return RegistrationCancelSerializer
        return RegistrationSerializer

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        registration = self.get_object()
        serializer = self.get_serializer(registration, data={}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(RegistrationSerializer(registration).data, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------
# Organizer — who registered for their event
# GET /registrations/organizer/events/{event_pk}/registrations/
# ---------------------------------------------------------------------
class RegistrationOrganizerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RegistrationOrganizerSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizer, IsEventOwner]

    def _get_event(self):
        return get_object_or_404(Event, pk=self.kwargs["event_pk"], organizer=self.request.user)

    def get_queryset(self):
        return (
            Registration.objects.filter(event=self._get_event())
            .select_related("participant", "stage", "event")
        )
