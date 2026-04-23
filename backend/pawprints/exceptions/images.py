from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pawprints.exceptions import ServiceError


class ImageFileError(ServiceError):
    """9001 - Generic Image File Error"""

    def __init__(
        self,
        message: str = "Image File Error",
        *,
        context: Mapping[str, Any] | None = None,
    ):
        super().__init__(code="9000", message=message, status_code=500, context=context)


class ImageFileTypeError(ServiceError):
    """9001 - Image file type error"""

    def __init__(
        self,
        message: str = "Uploaded image file type not supported",
        *,
        context: Mapping[str, Any] | None = None,
    ):
        super().__init__(code="9001", message=message, status_code=400, context=context)
