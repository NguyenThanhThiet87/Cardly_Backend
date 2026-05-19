from fastapi import HTTPException


class InvalidImageFormat(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Invalid image format. Supported: jpeg, png, webp")


class FileTooLarge(HTTPException):
    def __init__(self):
        super().__init__(status_code=413, detail="File too large. Max size: 5MB")


class OcrFailed(HTTPException):
    def __init__(self):
        super().__init__(status_code=422, detail="OCR processing failed")
