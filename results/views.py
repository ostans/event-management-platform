from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import (
    IsEventOwner,
    IsOrganizer,
    IsParticipant,
)
from events.models import Event
from registrations.models import Registration

from .models import Feedback, Result
from .serializers import (
    FeedbackCreateSerializer,
    FeedbackOrganizerSerializer,
    FeedbackSerializer,
    ResultOrganizerSerializer,
    ResultPublicSerializer,
    ResultWriteSerializer,
)


class ResultPublicViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = ResultPublicSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        event = get_object_or_404(Event, pk=self.kwargs["event_pk"])
        return Result.objects.filter(event=event, is_published=True).select_related("participant", "stage")


class ResultOrganizerViewSet(viewsets.ModelViewSet):

    permission_classes = [permissions.IsAuthenticated, IsOrganizer]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ResultWriteSerializer
        return ResultOrganizerSerializer

    def _get_event(self):
        return get_object_or_404(Event, pk=self.kwargs["event_pk"], organizer=self.request.user)

    def get_queryset(self):
        return Result.objects.filter(event=self._get_event()).select_related("participant", "stage")

    def perform_create(self, serializer):
        serializer.save(event=self._get_event())

    def get_permissions(self):
        if self.action in ("retrieve", "update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsOrganizer(), IsEventOwner()]
        return super().get_permissions()


class FeedbackAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated, IsParticipant]

    def _get_registration(self, request):
        return get_object_or_404(Registration, pk=self.kwargs["registration_pk"], participant=request.user)

    def get(self, request, *args, **kwargs):
        registration = self._get_registration(request)
        feedback = get_object_or_404(Feedback, registration)
        return Response(FeedbackSerializer(feedback).data)

    def post(self, request, *args, **kwargs):
        registration = self._get_registration(request)
        if hasattr(registration, "feedback"):
            return Response(
                {"detail": "for this registration feedback already exists."}, status=status.HTTP_409_CONFLICT
            )
        serializer = FeedbackCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(registration=registration)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FeedbackOrganizerViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizer, IsEventOwner]

    def _get_event(self):
        return get_object_or_404(Event, pk=self.kwargs["event_pk"], organizer=self.request.user)

    def get_queryset(self):
        return (
            Feedback.objects.filter(registration__event=self._get_event())
            .select_related("registration__participant")
            .order_by("-created_at")
        )
