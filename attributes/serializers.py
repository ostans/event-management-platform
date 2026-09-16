from datetime import date
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from events.models import EventType

from .models import VALUE_FIELDS, Attribute, EventAttributeValue


class AttributeSerializer(serializers.ModelSerializer):
    event_types = serializers.SlugRelatedField(
        slug_field="code",
        many=True,
        queryset=EventType.objects.all(),
        required=False,
    )

    class Meta:
        model = Attribute
        fields = ["id", "code", "name", "data_type", "description", "event_types"]


# ---------------------------------------------------------------------
# EventAttributeValue
#
# Clients never see/send the 5 raw value_* columns directly — they send
# a single `value` (as a string) plus the attribute's code, and this
# serializer casts it into the correct typed column based on
# attribute.data_type. On read, the same single `value` is reconstructed
# from whichever column is actually populated.
# ---------------------------------------------------------------------
class EventAttributeValueSerializer(serializers.ModelSerializer):
    attribute = serializers.SlugRelatedField(slug_field="code", queryset=Attribute.objects.all())
    value = serializers.CharField(
        write_only=True,
        help_text=("مقدار به‌صورت رشته ارسال می‌شود و بر اساس data_type ویژگی " "تبدیل و در ستون متناظر ذخیره می‌شود."),
    )

    class Meta:
        model = EventAttributeValue
        fields = ["id", "event", "attribute", "value"]

    # -- read side ------------------------------------------------------
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["data_type"] = instance.attribute.data_type
        data["value"] = self._read_typed_value(instance)
        return data

    @staticmethod
    def _read_typed_value(instance):
        for field_name in VALUE_FIELDS:
            value = getattr(instance, field_name)
            if value is not None:
                return value
        return None

    # -- write side -------------------------------------------------------
    def validate(self, attrs):
        attribute = attrs["attribute"]
        raw_value = attrs.pop("value")
        field_name = EventAttributeValue.FIELD_BY_DATA_TYPE[attribute.data_type]
        attrs[field_name] = self._parse_value(attribute.data_type, raw_value)
        return attrs

    @staticmethod
    def _parse_value(data_type, raw_value):
        try:
            if data_type == Attribute.DataType.INTEGER:
                return int(raw_value)
            if data_type == Attribute.DataType.DECIMAL:
                return Decimal(raw_value)
            if data_type == Attribute.DataType.BOOLEAN:
                lowered = raw_value.strip().lower()
                if lowered in ("true", "1", "yes", "بله"):
                    return True
                if lowered in ("false", "0", "no", "خیر"):
                    return False
                raise ValueError(raw_value)
            if data_type == Attribute.DataType.DATE:
                return date.fromisoformat(raw_value)
            return raw_value  # STRING
        except (ValueError, InvalidOperation):
            raise serializers.ValidationError({"value": f"مقدار با نوع '{data_type}' سازگار نیست: '{raw_value}'"})

    # -- full_clean() is not called automatically by DRF, so we call it
    #    explicitly here to enforce Model.clean() (exactly-one-value +
    #    data_type match + event_type scoping) before every save. --------
    def create(self, validated_data):
        instance = EventAttributeValue(**validated_data)
        self._run_full_clean(instance)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        # Reset every value_* column first, then set only the one that
        # applies — covers the case where attribute/data_type changed.
        for field_name in VALUE_FIELDS:
            setattr(instance, field_name, None)
        for key, val in validated_data.items():
            setattr(instance, key, val)
        self._run_full_clean(instance)
        instance.save()
        return instance

    @staticmethod
    def _run_full_clean(instance):
        try:
            instance.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict)


class EventAttributeValueWriteSerializer(EventAttributeValueSerializer):
    """Used under a nested /events/{event_pk}/attribute-values/ route,
    where `event` comes from the URL rather than the request body."""

    class Meta(EventAttributeValueSerializer.Meta):
        extra_kwargs = {"event": {"read_only": True}}
