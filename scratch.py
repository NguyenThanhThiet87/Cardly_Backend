import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

async def run():
    url = os.getenv('PADDLEOCR_VL_SERVER_URL', 'https://thietnt-paddleocr-vl-api.hf.space') + '/predict'
    token = os.getenv('ACCESS_TOKEN_PADDLEOCR_VL')
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    async with httpx.AsyncClient() as client:
        r = await client.post(url, headers=headers, files={'file': open('src/scans/sample/business_cards_mock_up_2.webp', 'rb')}, timeout=60)
        print("Status code:", r.status_code)
        try:
            print("Response JSON:", r.json())
        except:
            print("Response text:", r.text)

asyncio.run(run())
