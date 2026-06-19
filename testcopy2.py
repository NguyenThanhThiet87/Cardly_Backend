import json
import os
from dotenv import load_dotenv
from paddleocr import PaddleOCR
from google import genai
from google.genai.types import GenerateContentConfig
from paddleocr import PaddleOCRVL

# Tải cấu hình môi trường từ file .env
load_dotenv()

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# -------------------------------------------------------
# Inline JSON Schema không dùng $ref/$defs để Gemini
# có thể parse đúng nested structures
# -------------------------------------------------------
EXTRACTED_FIELD_SCHEMA = {
    "type": "object",
    "properties": {
        "value": {"type": "string", "nullable": True},
        "confidence": {"type": "number"}
    }
}

CONDITION_DESCRIPTION_SCHEMA = {
    "type": "object",
    "properties": {
        "condition": {"type": "string", "nullable": True},
        "description": {"type": "string", "nullable": True}
    }
}

DRIVER_LICENSE_SCHEMA = {
    "type": "object",
    "nullable": True,
    "properties": {
        "full_name":              EXTRACTED_FIELD_SCHEMA,
        "date_of_birth":          EXTRACTED_FIELD_SCHEMA,
        "licence_number":         EXTRACTED_FIELD_SCHEMA,
        "expiry_date":            EXTRACTED_FIELD_SCHEMA,
        "address":                EXTRACTED_FIELD_SCHEMA,
        "licence_class":          EXTRACTED_FIELD_SCHEMA,
        "conditions":             EXTRACTED_FIELD_SCHEMA,
        "condition_descriptions": {"type": "array", "items": CONDITION_DESCRIPTION_SCHEMA, "nullable": True},
        "state":                  EXTRACTED_FIELD_SCHEMA,
        "card_number":            EXTRACTED_FIELD_SCHEMA,
        "issue_date":             EXTRACTED_FIELD_SCHEMA,
    }
}

PASSPORT_SCHEMA = {
    "type": "object",
    "nullable": True,
    "properties": {
        "passport_number":  EXTRACTED_FIELD_SCHEMA,
        "given_names":      EXTRACTED_FIELD_SCHEMA,
        "surname":          EXTRACTED_FIELD_SCHEMA,
        "date_of_birth":    EXTRACTED_FIELD_SCHEMA,
        "date_of_issue":    EXTRACTED_FIELD_SCHEMA,
        "expiry_date":      EXTRACTED_FIELD_SCHEMA,
        "nationality":      EXTRACTED_FIELD_SCHEMA,
        "gender":           EXTRACTED_FIELD_SCHEMA,
        "place_of_birth":   EXTRACTED_FIELD_SCHEMA,
    }
}

MEDICARE_CARD_SCHEMA = {
    "type": "object",
    "nullable": True,
    "properties": {
        "medicare_card_number":      EXTRACTED_FIELD_SCHEMA,
        "medicare_card_first_name":  EXTRACTED_FIELD_SCHEMA,
        "medicare_card_middle_name": EXTRACTED_FIELD_SCHEMA,
        "medicare_card_last_name":   EXTRACTED_FIELD_SCHEMA,
        "medicare_card_expiry_date": EXTRACTED_FIELD_SCHEMA,
        "medicare_card_position":    EXTRACTED_FIELD_SCHEMA,
    }
}

UNIFIED_SCHEMA = {
    "type": "object",
    "properties": {
        "document_type": {
            "type": "string",
            "enum": ["driver_license", "passport", "medicare_card", "unknown"]
        },
        "driver_license":  DRIVER_LICENSE_SCHEMA,
        "passport":        PASSPORT_SCHEMA,
        "medicare_card":   MEDICARE_CARD_SCHEMA,
        "confidence":      {"type": "number"}
    },
    "required": ["document_type", "confidence"]
}

if __name__ == "__main__":
    # 1. Khởi tạo và chạy PaddleOCR cục bộ
    ocr = PaddleOCR(
        use_textline_orientation=True,
        lang='en',
    )

    image_path = "src\\features\\scans\\sample\\Australia-front-2-1024x609.jpg"
    print(f"{Colors.OKCYAN}Đang chạy PaddleOCR trên ảnh: {image_path}...{Colors.ENDC}")
    result = ocr.ocr(image_path)

    ocr_results = []
    for line in result[0]:
        bbox = line[0]
        text = line[1][0]
        confidence = float(line[1][1])
        ocr_results.append({
            "text": text,
            "confidence": confidence,
            "bbox": bbox
        })

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print(f"{Colors.FAIL}Lỗi: GEMINI_API_KEY chưa được thiết lập trong file .env!{Colors.ENDC}")
    else:
        try:
            client = genai.Client(api_key=api_key)

            prompt = f"""
            Analyze the following OCR text blocks extracted from an Australian identity document.
            Each block has a "text" field with the detected string, a "confidence" from the OCR engine, and a "bbox" (bounding box position).

            OCR Data:
            {json.dumps(ocr_results, indent=2, ensure_ascii=False)}

            Tasks:
            1. Classify the document type: 'driver_license', 'passport', 'medicare_card', or 'unknown'.
            2. Extract fields relevant to that document type from the OCR data.
            3. For each extracted field, assign a confidence score (0.0–1.0) based on how clearly the value appears in the OCR text.

            Rules:
            - Populate only the nested object matching the document type (e.g. 'driver_license'). Set the others to null.
            - Format all dates as YYYY-MM-DD.
            - If a field cannot be found or is unclear, set value to null and confidence to 0.0.
            - The root-level 'confidence' field should be the overall average confidence across all extracted fields.
            """

            response = client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=[prompt],
                config=GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=UNIFIED_SCHEMA,
                )
            )

            if response.usage_metadata:
                print(f"{Colors.WARNING}Token Usage: Prompt={response.usage_metadata.prompt_token_count}, "
                      f"Candidates={response.usage_metadata.candidates_token_count}, "
                      f"Total={response.usage_metadata.total_token_count}{Colors.ENDC}")

            extracted_data = json.loads(response.text.strip())

            print(f"\n{Colors.HEADER}--- KẾT QUẢ TRÍCH XUẤT (UNIFIED DOCUMENT EXTRACTION - HYBRID OCR) ---{Colors.ENDC}")
            print(json.dumps(extracted_data, indent=4, ensure_ascii=False))

        except Exception as e:
            print(f"{Colors.FAIL}Lỗi khi gọi API Gemini: {e}{Colors.ENDC}")