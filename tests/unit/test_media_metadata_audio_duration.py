"""Unit tests for audio_duration_seconds OGG parser implementation."""

import struct

from tg_auto_test.test_utils.media_metadata import audio_duration_seconds


def _build_ogg_page(granule: int, serial: int = 1, sequence: int = 0, payload: bytes = b"\x00") -> bytes:
    """Build a synthetic OGG page with given granule position."""
    num_segments = 1
    segment_table = bytes([len(payload)])
    header = b"OggS"  # capture pattern
    header += b"\x00"  # version
    header += b"\x00"  # header type
    header += struct.pack("<q", granule)  # granule position
    header += struct.pack("<I", serial)  # serial
    header += struct.pack("<I", sequence)  # sequence
    header += struct.pack("<I", 0)  # CRC (zeros ok)
    header += bytes([num_segments])  # number of segments
    header += segment_table
    header += payload
    return header


def test_audio_duration_seconds_valid_ogg() -> None:
    """Test audio_duration_seconds with valid OGG data."""
    page1 = _build_ogg_page(granule=48_000, sequence=0)  # 1 second
    page2 = _build_ogg_page(granule=96_000, sequence=1)  # 2 seconds
    ogg_data = page1 + page2

    duration = audio_duration_seconds(ogg_data)
    assert duration == 2.0


def test_audio_duration_seconds_empty_data() -> None:
    """Test audio_duration_seconds with empty data."""
    duration = audio_duration_seconds(b"")
    assert duration is None


def test_audio_duration_seconds_invalid_data() -> None:
    """Test audio_duration_seconds with non-OGG data."""
    duration = audio_duration_seconds(b"not ogg data")
    assert duration is None


def test_audio_duration_seconds_too_short() -> None:
    """Test audio_duration_seconds with data too short to be valid OGG."""
    duration = audio_duration_seconds(b"OggS\x00\x00")
    assert duration is None


def test_audio_duration_seconds_single_page() -> None:
    """Test audio_duration_seconds with single OGG page."""
    page = _build_ogg_page(granule=144_000)  # 3 seconds

    duration = audio_duration_seconds(page)
    assert duration == 3.0


def test_audio_duration_seconds_zero_granule() -> None:
    """Test audio_duration_seconds with zero granule position."""
    page = _build_ogg_page(granule=0)

    duration = audio_duration_seconds(page)
    assert duration is None


def test_audio_duration_seconds_negative_granule() -> None:
    """Test audio_duration_seconds with negative granule position (header page)."""
    page1 = _build_ogg_page(granule=-1, sequence=0)  # header page
    page2 = _build_ogg_page(granule=48_000, sequence=1)  # 1 second
    ogg_data = page1 + page2

    duration = audio_duration_seconds(ogg_data)
    assert duration == 1.0


def test_audio_duration_seconds_mixed_with_junk() -> None:
    """Test audio_duration_seconds with valid OGG pages mixed with junk data."""
    junk = b"some random bytes"
    page = _build_ogg_page(granule=192_000)  # 4 seconds
    more_junk = b"more junk"

    ogg_data = junk + page + more_junk

    duration = audio_duration_seconds(ogg_data)
    assert duration == 4.0


def test_audio_duration_seconds_corrupted_header() -> None:
    """Test audio_duration_seconds with corrupted OGG header."""
    # Start with valid page but truncate it
    page = _build_ogg_page(granule=48_000)
    corrupted = page[:20]  # truncate before full header

    duration = audio_duration_seconds(corrupted)
    assert duration is None


def test_audio_duration_seconds_multiple_pages_different_granules() -> None:
    """Test audio_duration_seconds with multiple pages having different granule positions."""
    page1 = _build_ogg_page(granule=24_000, sequence=0)  # 0.5 seconds
    page2 = _build_ogg_page(granule=72_000, sequence=1)  # 1.5 seconds
    page3 = _build_ogg_page(granule=120_000, sequence=2)  # 2.5 seconds
    ogg_data = page1 + page2 + page3

    duration = audio_duration_seconds(ogg_data)
    assert duration == 2.5
