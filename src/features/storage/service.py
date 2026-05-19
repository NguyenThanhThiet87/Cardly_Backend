import aioboto3
from uuid import uuid4

import os
from dotenv import load_dotenv

load_dotenv()

class StorageService:
    def __init__(self):
        self.bucket = os.getenv("AWS_S3_BUCKET")
        self.region = os.getenv("AWS_S3_REGION")
        
    async def upload_file(self, file_data: bytes, folder: str, original_name: str, content_type: str) -> str:
        # separate folder 
        extension = original_name.split('.')[-1]
        file_key = f"{folder}/{uuid4()}.{extension}"
        
        session = aioboto3.Session()
        async with session.client(
            's3',
            region_name=self.region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        ) as s3:
            await s3.put_object(
                Bucket=self.bucket,
                Key=file_key,
                Body=file_data,
                ContentType=content_type
            )
            return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{file_key}"
