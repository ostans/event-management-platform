import logging

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import (
    NotAuthenticated,
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)
    view = context.get("view", None)

    if response is None or response.status_code >= 500:
        logger.error(f"Unhandled exception in {view}: {exc}", exc_info=True)

    if isinstance(exc, ValidationError):
        return Response(
            {"status": "error", "message": "Invalid data", "error": response.data},
            status=status.HTTP_400_BAD_REQUEST,
        )
    elif isinstance(exc, NotAuthenticated):
        return Response(
            {"status": "failed", "message": "Authentication required"},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    elif isinstance(exc, (PermissionDenied, DjangoPermissionDenied)):
        return Response(
            {"status": "failed", "message": "Permission denied"},
            status=status.HTTP_403_FORBIDDEN,
        )
    elif isinstance(exc, Http404):
        return Response(
            {"status": "failed", "message": "Not found"},
            status=status.HTTP_404_NOT_FOUND,
        )
    elif response is None:
        return Response(
            {"status": "error", "message": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response
