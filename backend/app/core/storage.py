import os
import uuid
from pathlib import Path

import aiofiles

from app.config import settings

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}


def _get_upload_dir() -> Path:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def generate_unique_filename(original_filename: str) -> str:
    ext = Path(original_filename).suffix
    return f"{uuid.uuid4().hex}{ext}"


def validate_file_size(file_size: int) -> bool:
    return file_size <= settings.max_upload_size


def validate_mime_type(content_type: str) -> bool:
    return content_type in ALLOWED_MIME_TYPES


async def save_file(content: bytes, filename: str) -> str:
    """Save file to upload directory and return the relative path."""
    upload_dir = _get_upload_dir()
    unique_name = generate_unique_filename(filename)
    file_path = upload_dir / unique_name

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    return unique_name


async def read_file(filename: str) -> bytes:
    """Read file from upload directory."""
    file_path = _get_upload_dir() / filename

    async with aiofiles.open(file_path, "rb") as f:
        return await f.read()


async def delete_file(filename: str) -> bool:
    """Delete file from upload directory. Returns True if deleted, False if not found."""
    file_path = _get_upload_dir() / filename

    if file_path.exists():
        os.remove(file_path)
        return True
    return False
