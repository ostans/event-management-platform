from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from rest_framework import serializers

from events.models import Event, Stage

from .models import Registration


# ---------------------------------------------------------------------
# Read — a participant's own registrations
# ---------------------------------------------------------------------
class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:

        model = Registration
        fields = ["id", "event", "stage", "status", "created_at"]
        read_only_fields = fields


# ---------------------------------------------------------------------
# Read — organizer's view of who registered for their event
# ---------------------------------------------------------------------
class RegistrationOrganizerSerializer(serializers.ModelSerializer):
    participant_username = serializers.CharField(source="participant.phone_number", read_only=True)

    class Meta:
        model = Registration
        fields = [
            "id",
            "participant",
            "participant_username",
            "stage",
            "status",
            "created_at",
        ]
        read_only_fields = fields


# ---------------------------------------------------------------------
# Write — a participant registers for an event (or a stage of it)
# ---------------------------------------------------------------------
class RegistrationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = ["id", "event", "stage", "status", "created_at"]
        read_only_fields = ["id", "status", "created_at"]

    def validate(self, attrs):
        event = attrs["event"]
        stage = attrs.get("stage")

        if event.status != Event.Status.PUBLISHED:
            raise serializers.ValidationError("Only PUBLISHED events can be registered for.")

        if event.registration_scope == Event.RegistrationScope.STAGE:
            if stage is None:
                raise serializers.ValidationError(
                    {"stage": "Stage is required for events with stage-level registration scop"}
                )
            if stage.event_id != event.id:
                raise serializers.ValidationError({"stage": f"Stage {stage} does not belong to {event}"})
        else:
            if stage is not None:
                raise serializers.ValidationError(
                    {"stage": f"Stage is not required for events with event-level registration scope."}
                )

        return attrs

    def create(self, validated_data):
        participant = self.context["request"].user
        event = validated_data["event"]
        stage = validated_data.get("stage")

        with transaction.atomic():
            if stage is None:
                locked_event = Event.objects.select_for_update().get(pk=event.pk)
                capacity = locked_event.capacity
                current_count = Registration.objects.filter(
                    event=locked_event,
                    stage__isnull=True,
                    status=Registration.Status.REGISTERED,
                ).count()
            else:
                locked_stage = Stage.objects.select_for_update().get(pk=stage.pk)
                capacity = locked_stage.capacity
                current_count = Registration.objects.filter(
                    stage=locked_stage, status=Registration.Status.REGISTERED
                ).count()

            if capacity is not None and current_count >= capacity:
                raise serializers.ValidationError("Capacity for this event/stage has been reached.")

            instance = Registration(participant=participant, event=event, stage=stage)
            try:
                instance.full_clean()
            except DjangoValidationError as exc:
                raise serializers.ValidationError(exc.message_dict)

            try:
                instance.save()
            except IntegrityError:
                # Belt-and-suspenders: the partial unique indexes on
                # Registration are the final line of defense against a
                # race between two concurrent requests for the same
                # participant/event/stage.
                raise serializers.ValidationError("You have already registered for this event/stage.")

        return instance


# ---------------------------------------------------------------------
# Write — a participant cancels their own registration
# ---------------------------------------------------------------------
class RegistrationCancelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = ["id", "status"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        if self.instance.status == Registration.Status.CANCELLED:
            raise serializers.ValidationError("This registration has already been cancelled.")
        return attrs

    def update(self, instance, validated_data):
        instance.status = Registration.Status.CANCELLED
        instance.save(update_fields=["status", "updated_at"])
        return instance
