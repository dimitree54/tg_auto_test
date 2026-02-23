"""Extract audio/video metadata from in-memory bytes for tests."""

import struct


def audio_duration_seconds(data: bytes) -> float | None:
    """Return audio duration in seconds from bytes, or None if unavailable."""
    if not data:
        return None

    max_granule = _parse_ogg_max_granule(data)
    if max_granule is None or max_granule <= 0:
        return None

    return max_granule / 48_000.0


def _parse_ogg_max_granule(data: bytes) -> int | None:
    """Parse OGG container and return maximum granule position found."""
    if len(data) < 27:
        return None

    max_granule = 0
    offset = 0
    data_len = len(data)

    while offset + 27 <= data_len:
        if data[offset : offset + 4] != b"OggS":
            offset += 1
            continue

        try:
            granule = struct.unpack_from("<q", data, offset + 6)[0]
            if granule >= 0:
                max_granule = max(max_granule, granule)

            num_segments = data[offset + 26]
            if offset + 27 + num_segments > data_len:
                break

            page_size = 27 + num_segments
            for i in range(num_segments):
                page_size += data[offset + 27 + i]

            offset += page_size

        except (struct.error, IndexError):
            break

    return max_granule if max_granule > 0 else None


def mp4_duration_and_dimensions(data: bytes) -> tuple[float | None, int | None, int | None]:
    """Return (duration_seconds, width, height) parsed from MP4 bytes."""
    duration: float | None = None
    width: int | None = None
    height: int | None = None

    moov = _find_child_box(data, b"moov")
    if moov is None:
        return (None, None, None)

    mvhd = _find_child_box(moov, b"mvhd")
    if mvhd is not None:
        duration = _parse_mvhd_duration(mvhd)

    for box_type, payload in _iter_boxes(moov):
        if box_type != b"trak":
            continue
        is_video = _trak_is_video(payload)
        if not is_video:
            continue
        width, height = _parse_tkhd_dimensions(payload)
        break

    return (duration, width, height)


def _iter_boxes(data: bytes) -> list[tuple[bytes, bytes]]:
    boxes: list[tuple[bytes, bytes]] = []
    offset = 0
    data_len = len(data)
    while offset + 8 <= data_len:
        size = struct.unpack_from(">I", data, offset)[0]
        box_type = data[offset + 4 : offset + 8]
        header_size = 8
        if size == 1:
            if offset + 16 > data_len:
                break
            size = struct.unpack_from(">Q", data, offset + 8)[0]
            header_size = 16
        if size < header_size or offset + size > data_len:
            break
        payload_start = offset + header_size
        payload_end = offset + size
        boxes.append((box_type, data[payload_start:payload_end]))
        offset += size
    return boxes


def _find_child_box(data: bytes, box_type: bytes) -> bytes | None:
    for current_type, payload in _iter_boxes(data):
        if current_type == box_type:
            return payload
    return None


def _parse_mvhd_duration(mvhd_payload: bytes) -> float | None:
    if len(mvhd_payload) < 20:
        return None
    version = mvhd_payload[0]
    if version == 1:
        if len(mvhd_payload) < 32:
            return None
        timescale = struct.unpack_from(">I", mvhd_payload, 20)[0]
        duration = struct.unpack_from(">Q", mvhd_payload, 24)[0]
    else:
        timescale = struct.unpack_from(">I", mvhd_payload, 12)[0]
        duration = struct.unpack_from(">I", mvhd_payload, 16)[0]
    if timescale == 0:
        return None
    return duration / timescale


def _trak_is_video(trak_payload: bytes) -> bool:
    mdia = _find_child_box(trak_payload, b"mdia")
    if mdia is None:
        return False
    hdlr = _find_child_box(mdia, b"hdlr")
    if hdlr is None or len(hdlr) < 12:
        return False
    return hdlr[8:12] == b"vide"


def _parse_tkhd_dimensions(trak_payload: bytes) -> tuple[int | None, int | None]:
    tkhd = _find_child_box(trak_payload, b"tkhd")
    if tkhd is None:
        return (None, None)
    version = tkhd[0]
    width_offset = 88 if version == 1 else 76
    height_offset = 92 if version == 1 else 80
    if len(tkhd) < height_offset + 4:
        return (None, None)
    width_fixed = struct.unpack_from(">I", tkhd, width_offset)[0]
    height_fixed = struct.unpack_from(">I", tkhd, height_offset)[0]
    return (width_fixed >> 16, height_fixed >> 16)
