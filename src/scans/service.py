import os
import base64
import httpx
from dotenv import load_dotenv

load_dotenv()

def encode_image_to_base64(img_path):
    with open(img_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

async def scan_card_service(img_path):
    base_url = os.getenv("PADDLEOCR_VL_SERVER_URL")
    url = base_url.rstrip("/") + "/layout-parsing"
    
    token = os.getenv("ACCESS_TOKEN_PADDLEOCR_VL")

    try:
        base64_image = encode_image_to_base64(img_path)

        payload = {
            "file": base64_image,
            "fileType": 0, # 0 cho Ảnh, 1 cho PDF
            "useDocOrientationClassify": True,
            "useDocUnwarping": False
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.status_code != 200:
                print(f"❌ Lỗi Server ({response.status_code}): {response.text}")
                return None
            
            result = response.json()
            return result.get('result', result)

    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return None