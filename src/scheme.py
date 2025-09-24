from pydantic import BaseModel, field_validator


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None