from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Attribute, EventAttributeValue


@admin.register(Attribute)
class AttributeAdmin(ModelAdmin):
    list_display = ["code", "name", "data_type"]
    search_fields = ["code", "name"]
    list_filter = ["event_types", "data_type"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(EventAttributeValue)
class EventAttributeValueAdmin(ModelAdmin):
    list_display = ["event", "attribute", "value"]
    search_fields = ["event", "attribute"]
    list_filter = ["event", "attribute__data_type"]
    readonly_fields = ["created_at", "updated_at"]
