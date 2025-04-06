from fastapi import HTTPException


class ValidationFailedException(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=422, detail=message)
