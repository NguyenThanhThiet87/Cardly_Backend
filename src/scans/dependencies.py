from fastapi import UploadFile
from .constants import SUPPORTED_FORMATS, MAX_FILE_SIZE
from .exceptions import InvalidImageFormat, FileTooLarge


async def validate_image_file(file: UploadFile) -> UploadFile:
    if file.content_type not in SUPPORTED_FORMATS:
        raise InvalidImageFormat()
    data = await file.read()
    if len(data) > MAX_FILE_SIZE:
        raise FileTooLarge()
    await file.seek(0)
    return file
