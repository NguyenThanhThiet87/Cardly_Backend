from pydantic import BaseModel, Field, field_validator, HttpUrl


class ScanResponse(BaseModel):
    text: str | None = None
    full_name: str | None = None
    position: str | None = None
    company: str | None = None
    phones: list[str] = []
    emails: str | None = None
    website: HttpUrl | None = None
    social_links: dict[str, HttpUrl] = {}
    address: str | None = None
    qr_code: HttpUrl | None = None

    # Helper để validate phone numbers extracted from regex
    @field_validator('phone', mode='before')
    @classmethod
    def validate_phone_list(cls, v):
        if isinstance(v, str):
            # If a single string is passed, wrap it in a list
            return [v] if v else []
        if v is None:
            return []
        return v

    @field_validator('address', mode='before')
    @classmethod
    def validate_address(cls, v):
        if isinstance(v, list):
            # Join list elements with comma and space if it's a list of strings
            return ", ".join(map(str, v))
        return v

    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v):
        if isinstance(v, list):
            # Return the first email if multiple are found
            return v[0] if v else None
        return v
