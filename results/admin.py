from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Feedback, Result


@admin.register(Result)
class ResultAdmin(ModelAdmin):
    list_display = ["event", "is_published", "created_at"]
    search_fields = ["event"]
    list_filter = ["is_published", "created_at"]


@admin.register(Feedback)
class FeedbackAdmin(ModelAdmin):
    list_display = ["registration__event", "rating", "comment", "created_at"]
    search_fields = ["registration__event", "registration__participant", "comment"]
    list_filter = ["rating", "created_at"]
