"""Storage adapters: local development and optional S3-compatible object storage."""
from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse


class StorageConfigurationError(RuntimeError):
    pass


class LocalStorage:
    """Local adapter for development only; not durable on Vercel/serverless hosts."""
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        if not isinstance(key, str) or not key or key.startswith("/") or "\\" in key:
            raise ValueError("Invalid storage key")
        path = (self.root / key).resolve()
        if self.root not in path.parents:
            raise ValueError("Invalid storage key")
        return path

    def put_file(self, key: str, filename: str) -> str:
        import shutil
        target = self._path(key)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(filename, target)
        return key

    def get_file(self, key: str, filename: str) -> str:
        import shutil
        source = self._path(key)
        if not source.is_file():
            raise FileNotFoundError(key)
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, filename)
        return filename

    def exists(self, key: str) -> bool:
        return self._path(key).is_file()

    def delete(self, key: str) -> None:
        path = self._path(key)
        if path.exists():
            path.unlink()


class S3Storage:
    """S3-compatible adapter using boto3; provider credentials stay server-side."""
    def __init__(self, endpoint_url: str, bucket: str, access_key: str, secret_key: str, region: str = "auto"):
        if not endpoint_url or not bucket or not access_key or not secret_key:
            raise StorageConfigurationError("Storage configuration is incomplete")
        parsed = urlparse(endpoint_url)
        if parsed.scheme != "https" and os.getenv("ALLOW_INSECURE_STORAGE_ENDPOINT") != "1":
            raise StorageConfigurationError("Storage endpoint must use HTTPS")
        import boto3
        from botocore.config import Config
        self.bucket = bucket
        self.client = boto3.client(
            "s3", endpoint_url=endpoint_url, region_name=region,
            aws_access_key_id=access_key, aws_secret_access_key=secret_key,
            config=Config(signature_version="s3v4", connect_timeout=5, read_timeout=30, retries={"max_attempts": 3}),
        )

    def _validate_key(self, key: str) -> str:
        if not isinstance(key, str) or not key or key.startswith("/") or "\\" in key or any(p in {"", ".", ".."} for p in key.split("/")):
            raise ValueError("Invalid storage key")
        return key

    def presign_upload(self, key: str, content_type: str, expires_seconds: int = 300) -> str:
        if expires_seconds < 30 or expires_seconds > 900:
            raise ValueError("Invalid URL lifetime")
        return self.client.generate_presigned_url(
            "put_object", Params={"Bucket": self.bucket, "Key": self._validate_key(key), "ContentType": content_type},
            ExpiresIn=expires_seconds,
        )

    def presign_download(self, key: str, expires_seconds: int = 180) -> str:
        if expires_seconds < 30 or expires_seconds > 900:
            raise ValueError("Invalid URL lifetime")
        return self.client.generate_presigned_url(
            "get_object", Params={"Bucket": self.bucket, "Key": self._validate_key(key)}, ExpiresIn=expires_seconds,
        )

    def put_file(self, key: str, filename: str) -> str:
        key = self._validate_key(key)
        self.client.upload_file(filename, self.bucket, key)
        return key

    def get_file(self, key: str, filename: str) -> str:
        key = self._validate_key(key)
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        self.client.download_file(self.bucket, key, filename)
        return filename

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=self._validate_key(key))
            return True
        except self.client.exceptions.ClientError as exc:
            if exc.response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 404:
                return False
            raise

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=self._validate_key(key))


def storage_from_env():
    backend = os.getenv("STORAGE_BACKEND", "local").strip().lower()
    if backend == "local":
        if os.getenv("VERCEL"):
            raise StorageConfigurationError("Local storage is not durable on Vercel. Configure STORAGE_BACKEND=s3.")
        return LocalStorage(os.getenv("LOCAL_STORAGE_DIR", "var/media"))
    if backend == "s3":
        return S3Storage(
            endpoint_url=os.getenv("STORAGE_ENDPOINT", ""),
            bucket=os.getenv("STORAGE_BUCKET", ""),
            access_key=os.getenv("STORAGE_ACCESS_KEY_ID", ""),
            secret_key=os.getenv("STORAGE_SECRET_ACCESS_KEY", ""),
            region=os.getenv("STORAGE_REGION", "auto"),
        )
    raise StorageConfigurationError("Unsupported STORAGE_BACKEND")
