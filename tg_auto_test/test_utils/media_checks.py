import io
from pathlib import Path

from PIL import Image


def image_size_from_bytes(image_bytes: bytes) -> tuple[int, int]:
    with Image.open(io.BytesIO(image_bytes)) as image:
        return image.size


def image_size_from_path(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        return image.size


def file_size(path: Path) -> int:
    return path.stat().st_size
