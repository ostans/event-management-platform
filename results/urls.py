from django.urls import path
from rest_framework_nested import routers

from events.urls import router as events_router

from .views import (
    FeedbackAPIView,
    FeedbackOrganizerViewSet,
    ResultOrganizerViewSet,
    ResultPublicViewSet,
)

public_events_router = routers.NestedDefaultRouter(events_router, "public/events", lookup="even")
public_events_router.register("results", ResultPublicViewSet, basename="public-event-results")

organizer_events_router = routers.NestedDefaultRouter(events_router, "organizer/events", lookup="event")
organizer_events_router.register("results", ResultOrganizerViewSet, basename="organizer-event-results")
organizer_events_router.register("feedbacks", FeedbackOrganizerViewSet, basename="organizer-event-feedbacks")

urlpatterns = (
    public_events_router.urls
    + organizer_events_router.urls
    + [
        path(
            "participant/registrations/<int:registration_pk>/feedback/",
            FeedbackAPIView.as_view(),
            name="registrtion-feedback",
        ),
    ]
)
