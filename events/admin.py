from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Event, EventType, Stage, StageAssignment, StageRoleType


@admin.register(Event)
class EventAdmin(ModelAdmin):
    list_display = ["title", "organizer", "event_type", "start_time", "end_time", "status"]
    search_fields = ["title", "organizer__full_name", "event_type__name"]
    list_filter = ["status", "start_time", "end_time", "event_type", "created_at", "updated_at"]


@admin.register(EventType)
class EventTypeAdmin(ModelAdmin):
    list_display = ["name", "code"]
    search_fields = ["name", "code"]
    ordering = ["code"]


admin.site.register(StageRoleType)


@admin.register(Stage)
class StageAdmin(ModelAdmin):
    list_display = ["event", "order_index", "title", "event__organizer", "start_time", "end_time"]
    search_fields = ["event__title", "title"]
    list_filter = ["event", "start_time"]


@admin.register(StageAssignment)
class StageAssignmentAdmin(ModelAdmin):
    list_display = ["stage", "role_type", "guest_name"]
