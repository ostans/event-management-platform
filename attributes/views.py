from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets

from events.models import Event
from core.permissions import IsOrganizer

from .models import Attribute, EventAttributeValue
from .serializers import (
    AttributeSerializer,
    EventAttributeValueSerializer,
    EventAttributeValueWriteSerializer,
)


# ---------------------------------------------------------------------
# Attribute — shared metadata, not owned by a single organizer.
# Anyone can read the catalog; only organizers can define new ones.
# ---------------------------------------------------------------------
class AttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.prefetch_related("event_types")
    serializer_class = AttributeSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsOrganizer()]


# ---------------------------------------------------------------------
# EventAttributeValue — public read (published events only)
# GET /public/events/{event_pk}/attribute-values/
# ---------------------------------------------------------------------
class EventAttributeValuePublicViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EventAttributeValueSerializer
    permission_classes = [permissions.AllowAny]

    def _get_event(self):
        return get_object_or_404(Event, pk=self.kwargs["event_pk"], status=Event.Status.PUBLISHED)

    def get_queryset(self):
        return EventAttributeValue.objects.filter(event=self._get_event()).select_related("attribute")


# ---------------------------------------------------------------------
# EventAttributeValue — organizer read/write (own events only)
# /organizer/events/{event_pk}/attribute-values/
# ---------------------------------------------------------------------
class EventAttributeValueOrganizerViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return EventAttributeValueWriteSerializer
        return EventAttributeValueSerializer

    def _get_event(self):
        return get_object_or_404(Event, pk=self.kwargs["event_pk"], organizer=self.request.user)

    def get_queryset(self):
        return EventAttributeValue.objects.filter(event=self._get_event()).select_related("attribute")

    def perform_create(self, serializer):
        serializer.save(event=self._get_event())
