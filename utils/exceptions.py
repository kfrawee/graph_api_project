import logging

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        return response

    # Log the unexpected exception
    view = context.get("view", None)
    logger.error(f"Unhandled exception in view: {view}", exc_info=exc)

    return Response(
        {
            "error": "An unexpected error occurred.",
            "details": str(exc) if settings.DEBUG else None,
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
