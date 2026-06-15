from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from typing import List, Optional
from pydantic import BaseModel, Field


# =========================================================
# COMMON BASE
# =========================================================

class DocumentImage(BaseModel):
    file_name: Optional[str] = None
    file_url: Optional[str] = None


# =========================================================
# AUSTRALIAN PASSPORT
# =========================================================

class AustralianPassport(BaseModel):
    australian_passport_first_name: str = Field(
        ...,
        description="Given name(s) as shown on the Australian passport"
    )

    australian_passport_middle_name: Optional[str] = Field(
        None,
        description="Middle name as shown on the Australian passport"
    )

    australian_passport_last_name: str = Field(
        ...,
        description="Surname as shown on the Australian passport"
    )

    australian_passport_number: str = Field(
        ...,
        description="Passport number (e.g. RA0123456)"
    )

    australian_passport_date_of_birth: str = Field(
        ...,
        description="Date of birth"
    )

    australian_passport_date_of_issue: str = Field(
        ...,
        description="Passport issue date"
    )

    australian_passport_expiry_date: str = Field(
        ...,
        description="Passport expiry date"
    )

    australian_passport_nationality: str = Field(
        ...,
        description="Nationality (e.g. AUSTRALIAN)"
    )

    australian_passport_gender: str = Field(
        ...,
        description="Gender (M, F, X)"
    )

    australian_passport_place_of_birth: str = Field(
        ...,
        description="Place of birth"
    )

    commencement_document_front: List[DocumentImage] = Field(
        ...,
        description="Passport front/data page image(s)"
    )

    commencement_document_back: Optional[List[DocumentImage]] = Field(
        default=None,
        description="Passport back/observation page image(s)"
    )


# =========================================================
# AUSTRALIAN DRIVER LICENSE
# =========================================================

class AustralianDriverLicense(BaseModel):
    australian_driver_license_first_name: str = Field(
        ...,
        description="Driver license first name"
    )

    australian_driver_license_middle_name: Optional[str] = Field(
        None,
        description="Driver license middle name"
    )

    australian_driver_license_last_name: str = Field(
        ...,
        description="Driver license last name"
    )

    australian_driver_license_address: str = Field(
        ...,
        description="Residential address"
    )

    australian_driver_license_licence_number: str = Field(
        ...,
        description="License number"
    )

    australian_driver_license_state: str = Field(
        ...,
        description="Australian state or territory"
    )

    australian_driver_license_card_number: str = Field(
        ...,
        description="Card number on back side"
    )

    australian_driver_license_class: str = Field(
        ...,
        description="License class"
    )

    australian_driver_license_expiry_date: str = Field(
        ...,
        description="License expiry date"
    )

    australian_driver_license_dob: str = Field(
        ...,
        description="Date of birth"
    )

    primary_document_front: List[DocumentImage] = Field(
        ...,
        description="Front side image(s)"
    )

    primary_document_back: List[DocumentImage] = Field(
        ...,
        description="Back side image(s)"
    )


# =========================================================
# MEDICARE CARD
# =========================================================

class MedicareCard(BaseModel):
    medicare_card_number: str = Field(
        ...,
        description="10-digit Medicare card number"
    )

    medicare_card_first_name: str = Field(
        ...,
        description="First name"
    )

    medicare_card_middle_name: Optional[str] = Field(
        None,
        description="Middle name or initial"
    )

    medicare_card_last_name: str = Field(
        ...,
        description="Last name"
    )

    medicare_card_expiry_date: str = Field(
        ...,
        description="Expiry date MM/YYYY"
    )

    medicare_card_position: str = Field(
        ...,
        description="Position number on card"
    )

    secondary_document_front: List[DocumentImage] = Field(
        ...,
        description="Front side image(s)"
    )

    secondary_document_back: Optional[List[DocumentImage]] = Field(
        default=None,
        description="Back side image(s)"
    )
    
class ExtractedCardData(BaseModel):
    full_name: Optional[str] = None
    position: Optional[str] = None
    company: Optional[str] = None
    phones: Optional[list[str]] = None
    emails: Optional[list[str]] = None
    website: Optional[str] = None
    address: Optional[str] = None
    confidence: Optional[float] = None

class ScanResponse(BaseModel):
    id: str = Field(alias="_id")
    image_url: str
    status: str
    raw_text: Optional[str] = None
    extracted_data: Optional[ExtractedCardData] = None
    created_at: datetime
