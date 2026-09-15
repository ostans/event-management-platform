from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.exceptions import ValidationError

from core.permissions import IsEventOwner, IsOrganizer

from .models import Event, EventType, Stage, StageAssignment, StageRoleType
from .serializers import (
    EventOrganizerSerializer,
    EventPublicDetailSerializer,
    EventPublicListSerializer,
    EventTypeSerializer,
    StageAssignmentSerializer,
    StageRoleTypeSerializer,
    StageSerializer,
)


class EventTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer
    permission_classes = [permissions.AllowAny]


class StageRoleTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = StageRoleType.objects.all()
    serializer_class = StageRoleTypeSerializer
    permission_classes = [permissions.AllowAny]


class EventPublicViewSet(viewsets.ReadOnlyModelViewSet):

    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Event.objects.filter(status=Event.Status.PUBLISHED).select_related("event_type")

    def get_serializer_class(self):
        if self.action == "retrieve":
            return EventPublicDetailSerializer
        return EventPublicListSerializer


class EventOrganizerViewSet(viewsets.ModelViewSet):

    serializer_class = EventOrganizerSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def get_queryset(self):
        return (
            Event.objects.filter(organizer=self.request.user)
            .select_related("event_type")
            .prefetch_related("stages", "stages__assignments")
        )

    def get_permissions(self):
        if self.action in ("retrieve", "update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsOrganizer(), IsEventOwner()]
        return super().get_permissions()

    def perform_destroy(self, instance):
        if instance.status != Event.Status.DRAFT:
            raise ValidationError("Only draft events can be deleted. Close the event instead.")
        instance.delete()


class StageOrganizerViewSet(viewsets.ModelViewSet):

    serializer_class = StageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def _get_event(self):
        return get_object_or_404(Event, pk=self.kwargs["event_pk"], organizer=self.request.user)

    def get_queryset(self):
        return Stage.objects.filter(event=self._get_event()).prefetch_related("assignments")

    def perform_create(self, serializer):
        serializer.save(event=self._get_event())


class StageAssignmentOrganizerViewSet(viewsets.ModelViewSet):

    serializer_class = StageAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def _get_stage(self):
        return get_object_or_404(
            Stage,
            pk=self.kwargs["stage_pk"],
            event_id=self.kwargs["event_pk"],
            event__organizer=self.request.user,
        )

    def get_queryset(self):
        return StageAssignment.objects.filter(stage=self._get_stage())

    def perform_create(self, serializer):
        serializer.save(stage=self._get_stage())
