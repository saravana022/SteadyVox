"""SteadyVox Object Storage Service.

Manages audio uploads and downloads via AWS S3 / MinIO with local filesystem fallback.
"""

import os
import uuid
from pathlib import Path
from typing import Optional
import boto3
from botocore.exceptions import ClientError, EndpointConnectionError

from backend.app.core.config import settings


class StorageService:
    def __init__(self):
        self.bucket_name = settings.S3_BUCKET_NAME
        self.endpoint_url = settings.S3_ENDPOINT_URL
        self.access_key = settings.S3_ACCESS_KEY
        self.secret_key = settings.S3_SECRET_KEY
        self.region = settings.S3_REGION
        self.use_ssl = settings.S3_USE_SSL

        # Fallback local directory
        self.local_storage_dir = Path("./storage/audio")
        self.local_storage_dir.mkdir(parents=True, exist_ok=True)

        self._s3_client = None
        self._s3_available = None

    def _get_client(self):
        if self._s3_client is None:
            self._s3_client = boto3.client(
                "s3",
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region,
                use_ssl=self.use_ssl,
            )
        return self._s3_client

    def is_s3_available(self) -> bool:
        if self._s3_available is not None:
            return self._s3_available
        try:
            client = self._get_client()
            client.head_bucket(Bucket=self.bucket_name)
            self._s3_available = True
        except Exception:
            try:
                # Try creating bucket if missing
                client = self._get_client()
                client.create_bucket(Bucket=self.bucket_name)
                self._s3_available = True
            except Exception:
                self._s3_available = False
        return self._s3_available

    def upload_audio(self, audio_bytes: bytes, filename: str) -> str:
        """Uploads audio file to S3/MinIO or local fallback. Returns object key."""
        ext = Path(filename).suffix or ".wav"
        s3_key = f"recordings/{uuid.uuid4()}{ext}"

        if self.is_s3_available():
            try:
                client = self._get_client()
                content_type = "audio/wav" if ext == ".wav" else "audio/mpeg"
                client.put_object(
                    Bucket=self.bucket_name,
                    Key=s3_key,
                    Body=audio_bytes,
                    ContentType=content_type,
                )
                return s3_key
            except Exception as e:
                print(f"S3 upload failed ({e}), using local storage fallback.")

        # Fallback to local disk
        local_path = self.local_storage_dir / s3_key
        local_path.parent.mkdir(parents=True, exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(audio_bytes)
        return s3_key

    def get_audio_bytes(self, s3_key: str) -> Optional[bytes]:
        """Retrieves raw audio bytes from S3 or local storage."""
        if self.is_s3_available():
            try:
                client = self._get_client()
                response = client.get_object(Bucket=self.bucket_name, Key=s3_key)
                return response["Body"].read()
            except Exception:
                pass

        # Check local storage fallback
        local_path = self.local_storage_dir / s3_key
        if local_path.exists():
            with open(local_path, "rb") as f:
                return f.read()
        return None

    def get_presigned_url(self, s3_key: str, expires_in: int = 3600) -> str:
        """Generates a presigned GET URL for client playback, or local endpoint url."""
        if self.is_s3_available():
            try:
                client = self._get_client()
                url = client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket_name, "Key": s3_key},
                    ExpiresIn=expires_in,
                )
                return url
            except Exception:
                pass
        return f"/api/v1/history/audio-file?key={s3_key}"


storage_service = StorageService()
