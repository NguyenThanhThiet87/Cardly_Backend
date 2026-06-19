from datetime import datetime, timezone
import json

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder

from ...core.database import get_db
from ...features.contacts.service import get as get_contact
from .models import EnrichmentResultDocument
from .schemas import EnrichmentResultCreate, EnrichmentResultUpdate

import os
from google import genai
from google.genai.types import Tool, GenerateContentConfig

from dotenv import load_dotenv
load_dotenv()

# crawl
import requests
from bs4 import BeautifulSoup

from .schemas import EnrichmentResultBase

COLLECTION = "enrichment_results"

def _encode(doc):
    return jsonable_encoder(doc, custom_encoder={ObjectId: str})


def _object_id(value: str, name: str) -> ObjectId:
    try:
        return ObjectId(value)
    except InvalidId:
        raise HTTPException(status_code=400, detail=f"Invalid {name}")


async def _ensure_contact_owner(contact_id: str, owner_id: str) -> None:
    contact = await get_contact(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    if str(contact["owner_id"]) != owner_id:
        raise HTTPException(status_code=403, detail="Access denied")


async def create(data: EnrichmentResultCreate, owner_id: str) -> dict:
    await _ensure_contact_owner(data.contact_id, owner_id)
    db = await get_db()
    doc = EnrichmentResultDocument(**data.model_dump())
    result_data = doc.model_dump(mode="json", exclude_none=True)
    result_data["contact_id"] = _object_id(data.contact_id, "contact ID")
    result = await db[COLLECTION].insert_one(result_data)
    created = await db[COLLECTION].find_one({"_id": result.inserted_id})
    return _encode(created)


async def get_by_contact(contact_id: str, owner_id: str) -> dict | None:
    await _ensure_contact_owner(contact_id, owner_id)
    db = await get_db()
    doc = await db[COLLECTION].find_one({"contact_id": {"$in": [contact_id, _object_id(contact_id, "contact ID")]}})
    return _encode(doc) if doc else None


async def update_by_contact(contact_id: str, owner_id: str, data: EnrichmentResultUpdate) -> dict | None:
    await _ensure_contact_owner(contact_id, owner_id)
    db = await get_db()
    update_data = {k: v for k, v in data.model_dump().items() if v is not None}
    update_data["updated_at"] = datetime.now(timezone.utc)
    doc = await db[COLLECTION].find_one_and_update(
        {"contact_id": {"$in": [contact_id, _object_id(contact_id, "contact ID")]}},
        {"$set": update_data},
        return_document=True,
    )
    return _encode(doc) if doc else None


async def delete_by_contact(contact_id: str, owner_id: str) -> bool:
    await _ensure_contact_owner(contact_id, owner_id)
    db = await get_db()
    result = await db[COLLECTION].delete_one({"contact_id": {"$in": [contact_id, _object_id(contact_id, "contact ID")]}})
    return result.deleted_count > 0


async def enrich(urls: list[str]) -> EnrichmentResultBase:
    # Lấy API Key từ .env
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment variables")

    try:
        # Truyền api_key trực tiếp
        client = genai.Client(api_key=api_key)

        prompt = f"""
        You are a strict information extraction engine.

        Your task: Given ONLY the following list of URLs (websites, social media, etc.), extract factual professional or company information. Do NOT use any prior knowledge, assumptions, or information not explicitly present in the provided URLs.

        List of URLs to analyze:
        {urls}

        Extract and return ONLY these fields:

        1. professional_brief
        - Write a concise professional/company summary (2–4 sentences)
        - Use ONLY facts explicitly found in the provided URLs
        - Do NOT add assumptions or external knowledge

        2. keywords
        - Return concise professional keywords/tags
        - Include ONLY terms directly supported by the source content

        3. highlights
        - Return notable factual highlights explicitly mentioned in the sources

        STRICT RULES:
        - Do NOT hallucinate or invent facts
        - Do NOT use prior knowledge
        - Do NOT guess or infer missing information
        - If information is unclear or unsupported, omit it
        - If no reliable information exists, return empty arrays or empty strings
        - Every extracted item must be traceable to the provided URLs only
        """

        # Gửi prompt cho Gemini
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=[prompt],
            config= GenerateContentConfig(
                response_mime_type="application/json",
                response_schema = EnrichmentResultBase.model_json_schema(),
                tools=[
                   {"url_context": {}},
                ],
            )
        )
        
        return EnrichmentResultBase.model_validate_json(response.text)
        
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        raise


