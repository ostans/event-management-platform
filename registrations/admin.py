from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Registration


@admin.register(Registration)
class RegistrationAdmin(ModelAdmin):
    list_display = ["event", "participant", "stage", "status"]
    search_fields = ["event__name", "participant__last_name"]
    list_filter = ["event", "status"]
