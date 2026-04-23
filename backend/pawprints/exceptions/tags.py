"""
Tag-related exceptions.
"""

from .base import ServiceError


class TagNotFoundError(ServiceError):
    """
    Raised when a tag is not found.

    Default HTTP status: 404
    Default error code: 8000
    """

    def __init__(self, message: str = "Tag not found.", context: dict | None = None):
        super().__init__(
            message=message,
            error_code=8000,
            http_status=404,
            context=context or {},
        )


class TagAlreadyExistsError(ServiceError):
    """
    Raised when attempting to create a tag with a duplicate name.

    Default HTTP status: 409
    Default error code: 8001
    """

    def __init__(
        self, message: str = "Tag with this name already exists.", context: dict | None = None
    ):
        super().__init__(
            message=message,
            error_code=8001,
            http_status=409,
            context=context or {},
        )
