from rest_framework import serializers

from .models import Event, EventType, Stage, StageAssignment, StageRoleType


class EventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventType
        fields = "__all__"


class StageRoleTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = StageRoleType
        fields = "__all__"


class StageAssignmentSerializer(serializers.ModelSerializer):

    role_type = serializers.SlugRelatedField(slug_field="code", queryset=StageRoleType.objects.all())

    class Meta:
        model = StageAssignment
        fields = ["id", "guest_name", "guest_phone_number", "role_type"]

    def validate(self, attrs):
        if attrs.get("guest_name") is None and attrs.get("guest_phone_number") is None:
            raise serializers.ValidationError("Either guest_name or guest_phone_number is required.")
        return attrs


class StageSerializer(serializers.ModelSerializer):

    assignments = StageAssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = Stage
        fields = [
            "id",
            "event",
            "title",
            "description",
            "order_index",
            "start_time",
            "end_time",
            "capacity",
            "assignments",
        ]
        read_only_fields = ("event", "created_at", "updated_at")

    def validate(self, attrs):
        event = attrs.get("event") or getattr(self.instance, "event", None)
        start_time = attrs.get("start_time", getattr(self.instance, "start_time", None))
        end_time = attrs.get("end_time", getattr(self.instance, "end_time", None))
        capacity = attrs.get("capacity", getattr(self.instance, "capacity", None))

        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError("End time must be after start time.")

        if event.registration_scope == Event.RegistrationScope.STAGE and capacity is None:
            raise serializers.ValidationError("Capacity is required for stage-level registration.")
        if event.registration_scope == Event.RegistrationScope.EVENT and capacity is not None:
            raise serializers.ValidationError("Capacity is not allowed for event-level registration.")

        return attrs


class EventPublicListSerializer(serializers.ModelSerializer):
    event_type = serializers.SlugRelatedField(slug_field="code", read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "event_type",
            "start_time",
            "end_time",
            "registration_scope",
        ]


class EventPublicDetailSerializer(EventPublicListSerializer):
    stages = StageSerializer(many=True, read_only=True)

    class Meta(EventPublicListSerializer.Meta):
        fields = EventPublicListSerializer.Meta.fields + ["capacity", "stages"]


class EventOrganizerSerializer(serializers.ModelSerializer):
    stages = StageSerializer(many=True, read_only=True)
    organizer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "organizer",
            "event_type",
            "title",
            "description",
            "start_time",
            "end_time",
            "registration_scope",
            "capacity",
            "status",
            "created_at",
            "updated_at",
            "stages",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, attrs):
        start_time = attrs.get("start_time", getattr(self.instance, "start_time", None))
        end_time = attrs.get("end_time", getattr(self.instance, "end_time", None))
        scope = attrs.get(
            "registration_scope",
            getattr(self.instance, "registration_scope", Event.RegistrationScope.EVENT),
        )
        capacity = attrs.get("capacity", getattr(self.instance, "capacity", None))

        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError("End time must be after start time.")

        if scope == Event.RegistrationScope.EVENT and capacity is None:
            raise serializers.ValidationError("Capacity is required for event-level registration scope.")
        if scope == Event.RegistrationScope.STAGE and capacity is not None:
            raise serializers.ValidationError("Capacity is not allowed for stage-level registration scope.")

        if (
            self.instance
            and "registration_scope" in attrs
            and attrs["registration_scope"] != self.instance.registration_scope
            and self.instance.stages.exists()
        ):
            raise serializers.ValidationError("Cannot change registration scope when stages exist.")

        if self.instance and "status" in attrs and attrs["status"] != self.instance.status:
            allowed = Event.ALLOWED_TRANSITIONS.get(self.instance.status, set())
            if attrs["status"] not in allowed:
                raise serializers.ValidationError(
                    f"Cannot transition from {self.instance.status} to {attrs["status"]} status."
                )

        return attrs

    def create(self, validated_data):
        validated_data["organizer"] = self.context["request"].user
        return super().create(validated_data)
