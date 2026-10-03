from typing import TypedDict

from telethon.tl.types import TypeMessageEntity


class FileSendOptions(TypedDict, total=False):
    caption: str
    parse_mode: object
    formatting_entities: list[TypeMessageEntity] | None
    force_document: bool
    voice_note: bool
    video_note: bool
