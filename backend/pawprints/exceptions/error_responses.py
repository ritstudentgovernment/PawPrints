from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(..., description="A unique, stable error code.")
    message: str = Field(..., description="A human-readable message summarizing the error.")
    context: dict | list | None = Field(
        None, description="Optional additional details about the error."
    )


class ErrorResponse(BaseModel):
    detail: ErrorDetail
