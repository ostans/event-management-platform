from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import OrganizerProfile, ParticipantProfile


@admin.register(ParticipantProfile)
class ParticipantProfileAdmin(ModelAdmin):
    list_display = ["user", "full_name", "events_attended", "created_at", "updated_at"]
    search_fields = ["user__phone_number", "full_name"]
    list_filter = ["created_at", "updated_at", "events_attended"]


@admin.register(OrganizerProfile)
class OrganizerProfileAdmin(ModelAdmin):
    ordering = ["-created_at"]
    list_display = ["user", "full_name", "organization_name", "events_organized", "created_at", "updated_at"]
    search_fields = ["user__phone_number", "full_name", "organization_name"]
    list_filter = ["created_at", "updated_at", "events_organized"]
