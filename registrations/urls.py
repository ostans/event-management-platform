from rest_framework_nested import routers

from events.urls import router as events_router

from .views import RegistrationOrganizerViewSet, RegistrationViewSet

# ---------------------------------------------------------------------
# /registrations/ — a participant's own registrations.
#
# Registered with an empty prefix because config/urls.py already mounts
# this urls.py at "registrations/".
# ---------------------------------------------------------------------
router = routers.DefaultRouter()
router.register(r"", RegistrationViewSet, basename="registration")

# ---------------------------------------------------------------------
# /registrations/organizer/events/{event_pk}/registrations/
#
# Nested off events_router.registry (a plain list, populated at import
# time). Same pattern as attributes/urls.py — do not append to
# events_router.urls, which is cached once events/urls.py computes
# urlpatterns.
# Nested routes are listed first so "organizer" is not captured as a pk.
# ---------------------------------------------------------------------
organizer_events_router = routers.NestedDefaultRouter(events_router, "organizer/events", lookup="event")
organizer_events_router.register(
    "registrations",
    RegistrationOrganizerViewSet,
    basename="organizer-event-registration",
)

urlpatterns = organizer_events_router.urls + router.urls
