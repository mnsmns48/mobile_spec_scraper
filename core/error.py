from fastapi import HTTPException


class ValidationFailedException(HTTPException):
    def __init__(self, errors: list):
        error_messages = [f"Field '{error['loc'][0]}': {error['msg']}" for error in errors]
        super().__init__(
            status_code=422,
            detail={"error": "Validation failed", "details": error_messages}
        )
