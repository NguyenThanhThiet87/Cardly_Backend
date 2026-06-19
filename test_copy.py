import json
import math
import re
from datetime import datetime
from paddleocr import PaddleOCR

# ----------------------------------------------------
# 1. Utilities (bbox helpers & name splitter)
# ----------------------------------------------------
def bbox_to_rect(bbox):
    xs = [p[0] for p in bbox]
    ys = [p[1] for p in bbox]
    return {
        "x": min(xs),
        "y": min(ys),
        "w": max(xs) - min(xs),
        "h": max(ys) - min(ys)
    }

def center(rect):
    return (
        rect["x"] + rect["w"] / 2,
        rect["y"] + rect["h"] / 2
    )

def distance(rect1, rect2):
    c1 = center(rect1)
    c2 = center(rect2)
    return math.sqrt(
        (c1[0] - c2[0]) ** 2 +
        (c1[1] - c2[1]) ** 2
    )

def split_name(full_name: str) -> tuple[str, str, str]:
    parts = [p.strip() for p in full_name.split() if p.strip()]
    if len(parts) == 1:
        return parts[0], "", ""
    elif len(parts) == 2:
        return parts[0], "", parts[1]
    elif len(parts) > 2:
        return parts[0], " ".join(parts[1:-1]), parts[-1]
    return "", "", ""

# ----------------------------------------------------
# 2. Validation functions
# ----------------------------------------------------
def validate_full_name(text):
    text = text.strip()
    if len(text) < 3 or len(text) > 80:
        return False
    pattern = r"^[A-Z\s\-']+$"
    return bool(re.fullmatch(pattern, text))

def validate_licence_number(text):
    text = text.strip()
    pattern = r"^\d{8,10}$"
    return bool(re.fullmatch(pattern, text))

def validate_card_number(text):
    text = text.strip()
    pattern = r"^[A-Z0-9]{8,12}$"
    return bool(re.fullmatch(pattern, text))

def validate_date(text):
    try:
        datetime.strptime(text, "%d-%m-%Y")
        return True
    except:
        return False

def normalize_date(text):
    dt = datetime.strptime(text, "%d-%m-%Y")
    return dt.strftime("%Y-%m-%d")

def validate_expiry_date(text):
    if not validate_date(text):
        return False
    dt = datetime.strptime(text, "%d-%m-%Y")
    return dt.year > 2000

def validate_dob(text):
    if not validate_date(text):
        return False
    dob = datetime.strptime(text, "%d-%m-%Y")
    age = (datetime.now() - dob).days / 365
    return 16 <= age <= 100

VALID_CLASSES = {"CAR", "R", "LR", "MR", "HR", "HC", "MC"}
def validate_licence_class(text):
    return text.strip().upper() in VALID_CLASSES

# ----------------------------------------------------
# 3. Spatial parser & Special Extractors
# ----------------------------------------------------
def find_nearest_valid_text(keyword_item, items, validation_fn):
    keyword_rect = bbox_to_rect(keyword_item["bbox"])
    candidates = []
    
    for item in items:
        if item == keyword_item:
            continue
            
        rect = bbox_to_rect(item["bbox"])
        
        if (
            rect["x"] >= keyword_rect["x"] - 50 or
            rect["y"] >= keyword_rect["y"] - 50
        ):
            if validation_fn(item["text"]):
                dist = distance(keyword_rect, rect)
                candidates.append((dist, item))
            
    candidates.sort(key=lambda x: x[0])
    if candidates:
        return candidates[0][1]
    return None

def extract_state(results):
    states_map = {
        "VIC": "VIC", "VICTORIA": "VIC",
        "NSW": "NSW", "NEW SOUTH WALES": "NSW",
        "QLD": "QLD", "QUEENSLAND": "QLD",
        "WA": "WA", "WESTERN AUSTRALIA": "WA",
        "SA": "SA", "SOUTH AUSTRALIA": "SA",
        "TAS": "TAS", "TASMANIA": "TAS",
        "ACT": "ACT", "AUSTRALIAN CAPITAL TERRITORY": "ACT",
        "NT": "NT", "NORTHERN TERRITORY": "NT"
    }
    for item in results:
        text = item["text"].upper()
        for key, val in states_map.items():
            if key in text:
                return {
                    "value": val,
                    "confidence": item["confidence"]
                }
    return None

def extract_address(results, name_item, expiry_item):
    if not name_item or not expiry_item:
        return None
        
    name_rect = bbox_to_rect(name_item["bbox"])
    expiry_rect = bbox_to_rect(expiry_item["bbox"])
    
    address_lines = []
    confidences = []
    
    for item in results:
        if item == name_item or item == expiry_item:
            continue
        rect = bbox_to_rect(item["bbox"])
        
        # Nằm giữa phần dưới của Tên và phần trên của nhãn Expiry
        if name_rect["y"] + name_rect["h"] - 5 < rect["y"] < expiry_rect["y"] + 5:
            # Thuộc vùng địa chỉ phía bên trái/giữa của thẻ
            if rect["x"] < expiry_rect["x"] + 450:
                # Loại trừ các nhãn từ khóa như "DATE OF BIRTH", "LICENCE EXPIRY" khỏi địa chỉ
                text_upper = item["text"].upper()
                if all(kw not in text_upper for kw in ["DATE", "BIRTH", "EXPIRY", "LICENCE", "DRIVER"]):
                    address_lines.append(item["text"].strip())
                    confidences.append(item["confidence"])
                
    if address_lines:
        return {
            "value": " ".join(address_lines),
            "confidence": sum(confidences) / len(confidences)
        }
    return None

# ----------------------------------------------------
# 4. Main parser with Custom Key Mapping
# ----------------------------------------------------
def parse_driver_licence(results):
    parsed = {}
    
    # 1. Tìm các trường thô và các vật thể mốc (markers)
    name_item_obj = None
    expiry_item_obj = None
    
    licence_number_obj = None
    expiry_date_obj = None
    dob_obj = None
    class_obj = None
    card_number_obj = None
    
    # Quét qua các dòng để phân tích
    for item in results:
        text = item["text"].upper().strip()
        
        if "LICENCE NO" in text:
            val_item = find_nearest_valid_text(item, results, validate_licence_number)
            if val_item:
                licence_number_obj = val_item
                
        elif "LICENCE EXPIRY" in text:
            expiry_item_obj = item
            val_item = find_nearest_valid_text(item, results, validate_expiry_date)
            if val_item:
                expiry_date_obj = val_item
                
        elif "DATE OF BIRTH" in text:
            val_item = find_nearest_valid_text(item, results, validate_dob)
            if val_item:
                dob_obj = val_item
                
        elif "LICENCE TYPE" in text:
            val_item = find_nearest_valid_text(item, results, validate_licence_class)
            if val_item:
                class_obj = val_item
                
        elif "CARD NO" in text or "CARD NUMBER" in text:
            val_item = find_nearest_valid_text(item, results, validate_card_number)
            if val_item:
                card_number_obj = val_item
                
        elif validate_full_name(text):
            if not name_item_obj:
                if all(kw not in text for kw in ["DRIVER", "VICTORIA", "LICENCE", "DATE", "ROADS"]):
                    name_item_obj = item

    # 2. Xây dựng kết quả chuẩn theo yêu cầu trường
    # Tên (Họ, Tên, Tên đệm)
    if name_item_obj:
        full_name_str = name_item_obj["text"].strip()
        first, middle, last = split_name(full_name_str)
        conf = name_item_obj["confidence"]
        
        parsed["australian_driver_license_first_name"] = {"value": first, "confidence": conf}
        parsed["australian_driver_license_middle_name"] = {"value": middle, "confidence": conf} if middle else { "value": None, "confidence": conf }
        parsed["australian_driver_license_last_name"] = {"value": last, "confidence": conf}
    else:
        parsed["australian_driver_license_first_name"] = None
        parsed["australian_driver_license_middle_name"] = None
        parsed["australian_driver_license_last_name"] = None

    # Địa chỉ
    address_res = extract_address(results, name_item_obj, expiry_item_obj)
    parsed["australian_driver_license_address"] = address_res

    # Số bằng lái
    if licence_number_obj:
        parsed["australian_driver_license_licence_number"] = {
            "value": licence_number_obj["text"].strip(),
            "confidence": licence_number_obj["confidence"]
        }
    else:
        parsed["australian_driver_license_licence_number"] = None

    # Bang cấp bằng
    parsed["australian_driver_license_state"] = extract_state(results)

    # Card number (mặt sau hoặc front nếu có)
    if card_number_obj:
        parsed["australian_driver_license_card_number"] = {
            "value": card_number_obj["text"].strip(),
            "confidence": card_number_obj["confidence"]
        }
    else:
        # Fallback tìm kiếm thử ký tự chữ số ngẫu nhiên thỏa mãn card number ở góc dưới nếu có nhãn trống
        parsed["australian_driver_license_card_number"] = { "value": None, "confidence": 0.0 }

    # Loại bằng lái (Class)
    if class_obj:
        parsed["australian_driver_license_class"] = {
            "value": class_obj["text"].strip().upper(),
            "confidence": class_obj["confidence"]
        }
    else:
        parsed["australian_driver_license_class"] = None

    # Ngày hết hạn
    if expiry_date_obj:
        parsed["australian_driver_license_expiry_date"] = {
            "value": normalize_date(expiry_date_obj["text"]),
            "confidence": expiry_date_obj["confidence"]
        }
    else:
        parsed["australian_driver_license_expiry_date"] = None

    # Ngày sinh
    if dob_obj:
        parsed["australian_driver_license_dob"] = {
            "value": normalize_date(dob_obj["text"]),
            "confidence": dob_obj["confidence"]
        }
    else:
        parsed["australian_driver_license_dob"] = None

    return parsed

# ----------------------------------------------------
# 5. Pipeline Execution
# ----------------------------------------------------
if __name__ == "__main__":
    ocr = PaddleOCR(
        use_textline_orientation=True,
        lang='en',
    )
    
    image_path = "src\\features\scans\sample\Australia-front-2-1024x609.jpg"
    result = ocr.ocr(image_path)

    print(result)

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
    
    # print(ocr_results)
    
    print("\n--- OUTPUT AUSTRALIAN DRIVER LICENSE SCHEMA CHUẨN ---")