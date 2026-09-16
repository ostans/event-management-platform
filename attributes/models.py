from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from core.models import BaseModel
from events.models import Event, EventType

VALUE_FIELDS = [
    "value_string",
    "value_integer",
    "value_decimal",
    "value_boolean",
    "value_date",
]


def _exactly_one_value_filled_q():
    """Q object matching rows where exactly one of VALUE_FIELDS is
    non-null and all the others are null. CheckConstraint can't sum
    booleans portably in the ORM, so this is built as an OR of
    "this one is set AND every other one is null" clauses."""
    condition = Q()
    for chosen in VALUE_FIELDS:
        clause = Q(**{f"{chosen}__isnull": False})
        for other in VALUE_FIELDS:
            if other != chosen:
                clause &= Q(**{f"{other}__isnull": True})
        condition |= clause
    return condition


class Attribute(BaseModel):

    class DataType(models.TextChoices):
        STRING = "string", "String"
        INTEGER = "integer", "Integer"
        DECIMAL = "decimal", "Decimal"
        BOOLEAN = "boolean", "Boolean"
        DATE = "date", "Date"

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=250)
    data_type = models.CharField(max_length=10, choices=DataType.choices, default=DataType.STRING)
    description = models.TextField(blank=True, null=True)
    event_types = models.ManyToManyField(
        EventType,
        related_name="attributes",
        blank=True,
        help_text="Event types that this attribute is allowed for. If none are selected, the attribute is allowed for all event types.",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.code}"


class EventAttributeValue(BaseModel):

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="attribute_values")
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name="event_values")

    value_string = models.CharField(max_length=500, null=True, blank=True)
    value_integer = models.IntegerField(null=True, blank=True)
    value_decimal = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    value_boolean = models.BooleanField(null=True, blank=True)
    value_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ["event", "attribute"]
        constraints = [
            models.CheckConstraint(
                condition=_exactly_one_value_filled_q(),
                name="exactly_one_value_filled",
            )
        ]

    FIELD_BY_DATA_TYPE = {
        Attribute.DataType.STRING: "value_string",
        Attribute.DataType.INTEGER: "value_integer",
        Attribute.DataType.DECIMAL: "value_decimal",
        Attribute.DataType.BOOLEAN: "value_boolean",
        Attribute.DataType.DATE: "value_date",
    }

    @property
    def value(self):
        return getattr(self, self.FIELD_BY_DATA_TYPE[self.attribute.data_type])

    def __str__(self):
        return f"{self.event} - {self.attribute}"

    def clean(self):
        errors = {}

        filled = [f for f in VALUE_FIELDS if getattr(self, f) is not None]
        if len(filled) != 1:
            errors["__all__"] = "Just one of the value fields must be filled."
        elif self.attribute_id:
            expected_field = self.FIELD_BY_DATA_TYPE[self.attribute.data_type]
            if filled[0] != expected_field:
                errors[filled[0]] = (
                    f"Field '{filled[0]}' does not match attribute data type '{self.attribute.data_type}'."
                    f" Expected '{expected_field}'."
                )

        if self.attribute_id and self.event_id:
            scoped_types = self.attribute.event_types.all()
            if scoped_types.exists() and self.event.event_type not in scoped_types:
                errors["attribute"] = (
                    f"Attribute '{self.attribute.name}' is not allowed for event type " f"'{self.event.event_type}'."
                )

        if errors:
            raise ValidationError(errors)
