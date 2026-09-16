from rest_framework_nested import routers

from events.urls import router as events_router

from .views import (
    AttributeViewSet,
    EventAttributeValueOrganizerViewSet,
    EventAttributeValuePublicViewSet,
)

# ---------------------------------------------------------------------
# /attributes/ — flat top-level resource, own router.
#
# Deliberately NOT registered on events_router: that router's .urls
# property is cached the moment events/urls.py computes its own
# urlpatterns (router.urls + ...), so any registration added to it
# afterwards (from here) would silently never appear. A separate
# router avoids that trap entirely.
# ---------------------------------------------------------------------
attribute_router = routers.DefaultRouter()
attribute_router.register("attributes", AttributeViewSet, basename="attribute")

# ---------------------------------------------------------------------
# /public/events/{event_pk}/attribute-values/
#
# This only needs events_router.registry (a plain list, populated at
# import time) to find the "public/events" entry — unrelated to the
# .urls caching issue above, so referencing the same router here is safe.
# ---------------------------------------------------------------------
public_events_router = routers.NestedDefaultRouter(events_router, "public/events", lookup="event")
public_events_router.register(
    "attribute-values",
    EventAttributeValuePublicViewSet,
    basename="public-event-attribute-value",
)

# ---------------------------------------------------------------------
# /organizer/events/{event_pk}/attribute-values/
# ---------------------------------------------------------------------
organizer_events_router = routers.NestedDefaultRouter(events_router, "organizer/events", lookup="event")
organizer_events_router.register(
    "attribute-values",
    EventAttributeValueOrganizerViewSet,
    basename="organizer-event-attribute-value",
)

urlpatterns = attribute_router.urls + public_events_router.urls + organizer_events_router.urls
