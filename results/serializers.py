from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .models import Feedback, Result


class ResultPublicSerializer(serializers.ModelSerializer):

    participant_full_name = serializers.CharField(source="participant.get_full_name", read_only=True, default=None)

    class Meta:
        model = Result
        fields = [
            "id",
            "event",
            "stage",
            "participant",
            "participant_full_name",
            "rank",
            "score",
            "label",
            "description",
        ]
        read_only_fields = fields


class ResultOrganizerSerializer(ResultPublicSerializer):

    class Meta(ResultPublicSerializer.Meta):
        fields = ResultPublicSerializer.Meta.fields + ["is_published", "created_at"]


class ResultWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = [
            "id",
            "event",
            "stage",
            "participant",
            "rank",
            "score",
            "label",
            "description",
            "is_published",
        ]
        extra_kwargs = {"event": {"read_only": True}}

    def create(self, validated_data):
        instance = Result(**validated_data)
        self._run_full_clean(instance)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        self._run_full_clean(instance)
        instance.save()
        return instance

    @staticmethod
    def _run_full_clean(instance):
        try:
            instance.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict)


class FeedbackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["id", "registration", "rating", "comment", "created_at"]
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {"registration": {"read_only": True}}

    def create(self, validated_data):
        instance = Feedback(**validated_data)
        self._run_full_clean()
        instance.save()
        return instance

    @staticmethod
    def _run_full_clean(instance):
        try:
            instance.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict)


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["id", "registration", "rating", "comment", "created_at"]
        read_only_fields = fields


class FeedbackOrganizerSerializer(serializers.ModelSerializer):
    participant_full_name = serializers.SerializerMethodField(
        source="registration.participant.get_full_name", read_only=True
    )

    class Meta:
        model = Feedback
        fields = ["id", "registration", "participant_full_name", "rating", "comment", "created_at"]
        read_only_fields = fields
