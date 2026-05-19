from fastapi import HTTPException


class ContactNotFound(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Contact not found")


class ContactAccessDenied(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Access denied")
