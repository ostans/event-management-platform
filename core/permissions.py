from rest_framework.permissions import BasePermission


class IsStaffUser(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user


class IsOrganizer(BasePermission):
    """Grants access only to authenticated users with role='organizer'."""

    message = "You must be an organizer to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and getattr(request.user, "role", None) == "organizer"
        )


class IsEventOwner(BasePermission):
    """Object-level check: request.user must be the event's organizer.

    Works directly on Event instances, or on any related object that
    exposes `.event` (e.g. Stage) or `.stage.event` (e.g. StageAssignment).
    """

    message = "You must be the organizer of this event to perform this action."

    def has_object_permission(self, request, view, obj):
        event = self._resolve_event(obj)
        return event is not None and event.organizer_id == request.user.id

    @staticmethod
    def _resolve_event(obj):
        if hasattr(obj, "organizer_id"):
            return obj
        if hasattr(obj, "event_id"):
            return obj.event
        if hasattr(obj, "stage_id"):
            return obj.stage.event
        return None
