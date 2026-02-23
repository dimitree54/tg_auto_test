import io

from PIL import Image
from telethon.tl.types import (
    Document,
    TypeDocumentAttribute,
)


def make_document(
    file_id: str,
    size: int,
    mime_type: str,
    attributes: list[TypeDocumentAttribute],
) -> Document:
    return Document(
        id=hash(file_id) & 0x7FFFFFFFFFFFFFFF,
        access_hash=0,
        file_reference=b"",
        date=None,
        mime_type=mime_type,
        size=size,
        dc_id=1,
        attributes=attributes,
    )


def image_dimensions(data: bytes) -> tuple[int, int]:
    if not data:
        raise ValueError("Cannot extract image dimensions: empty data.")
    img = Image.open(io.BytesIO(data))
    return img.size
