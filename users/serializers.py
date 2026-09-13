from auditlog.models import LogEntry
from rest_framework import serializers

from .models import OrganizerProfile, ParticipantProfile


class BaseProfileSerializer(serializers.ModelSerializer):
    class Meta:
        read_only_fields = ["user", "created_at", "updated_at"]


class ParticipantProfileSerializer(BaseProfileSerializer):
    class Meta(BaseProfileSerializer.Meta):
        model = ParticipantProfile
        fields = "__all__"


class OrganizerProfileSerializer(BaseProfileSerializer):
    class Meta(BaseProfileSerializer.Meta):
        model = OrganizerProfile
        fields = "__all__"


class LogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LogEntry
        fields = "__all__"
