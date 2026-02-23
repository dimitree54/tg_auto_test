import mimetypes


def detect_content_type(
    filename: str,
    force_document: bool,
    voice_note: bool,
    video_note: bool,
) -> str:
    if voice_note:
        return "audio/ogg"
    if video_note:
        return "video/mp4"
    guessed = mimetypes.guess_type(filename)[0]
    if guessed is not None:
        return guessed
    if force_document:
        return "application/octet-stream"
    return "image/png"
