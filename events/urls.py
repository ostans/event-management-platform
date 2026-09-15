from django.urls import include, path
from rest_framework_nested import routers

from .views import (
    EventOrganizerViewSet,
    EventPublicViewSet,
    EventTypeViewSet,
    StageAssignmentOrganizerViewSet,
    StageOrganizerViewSet,
    StageRoleTypeViewSet,
)

router = routers.DefaultRouter()
router.register(r"event-types", EventTypeViewSet, basename="event-types")
router.register(r"stage-role-types", StageRoleTypeViewSet, basename="stage-role-types")
router.register(r"public/events", EventPublicViewSet, basename="public-events")
router.register(r"organizer/events", EventOrganizerViewSet, basename="organizer-events")

organizer_events_router = routers.NestedDefaultRouter(router, r"organizer/events", lookup="event")
organizer_events_router.register(r"stages", StageOrganizerViewSet, basename="organizer-evene-stage")

stages_router = routers.NestedDefaultRouter(organizer_events_router, "stages", lookup="stage")
stages_router.register(
    "assignments",
    StageAssignmentOrganizerViewSet,
    basename="organizer-stage-assignment",
)

urlpatterns = router.urls + organizer_events_router.urls + stages_router.urls
