import re


def extract_text_fields(raw_text: str) -> dict:
    result: dict = {}
    phone = re.search(r"(\+?\d[\d\s\-]{7,}\d)", raw_text)
    email = re.search(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", raw_text)
    website = re.search(r"(https?://[^\s]+|www\.[^\s]+)", raw_text)
    if phone:
        result["phones"] = [phone.group(1).strip()]
    if email:
        result["emails"] = [email.group(0)]
    if website:
        result["website"] = website.group(0)
    return result
