"""Unit tests for MP3 duration parsing in audio_duration_seconds."""

import struct

from tg_auto_test.test_utils.media_metadata import audio_duration_seconds


def _build_mp3_frame(bitrate_index: int = 9, sample_rate_index: int = 0, padding: int = 0) -> bytes:
    """Build a synthetic MP3 frame header with given parameters."""
    # MP3 frame header structure (32 bits):
    # Bits 31-21: Sync word (11 bits all set to 1)
    # Bits 20-19: MPEG version (11 = MPEG1)
    # Bits 18-17: Layer (01 = Layer III)
    # Bit 16: Protection (1 = no CRC)
    # Bits 15-12: Bitrate index
    # Bits 11-10: Sample rate index
    # Bit 9: Padding bit
    # Bit 8: Private bit
    # Bits 7-6: Channel mode
    # Bits 5-4: Mode extension
    # Bit 3: Copyright
    # Bit 2: Original
    # Bits 1-0: Emphasis

    # Build header bit by bit for clarity
    header = 0xFFF00000  # Sync word (bits 31-21): 0xFFF (11 bits all 1s)
    header |= 0x3 << 19  # MPEG version (bits 20-19): 11 = MPEG1
    header |= 0x1 << 17  # Layer (bits 18-17): 01 = Layer III
    header |= 0x1 << 16  # Protection bit (bit 16): 1 = no CRC
    header |= (bitrate_index & 0x0F) << 12  # Bitrate index (bits 15-12)
    header |= (sample_rate_index & 0x03) << 10  # Sample rate index (bits 11-10)
    header |= (padding & 0x01) << 9  # Padding bit (bit 9)

    # Pack as 32-bit big-endian
    frame_bytes = struct.pack(">I", header)

    # Calculate frame size for valid MP3 frame
    bitrates = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0]
    sample_rates = [44100, 48000, 32000, 0]

    if bitrate_index < len(bitrates) and sample_rate_index < len(sample_rates):
        bitrate = bitrates[bitrate_index] * 1000
        sample_rate = sample_rates[sample_rate_index]
        if bitrate > 0 and sample_rate > 0:
            frame_length = (144 * bitrate) // sample_rate + padding
            # Add appropriate payload
            payload_size = max(0, frame_length - 4)  # Subtract header size
            frame_bytes += b"\x00" * payload_size
    else:
        # Add minimal payload for invalid cases
        frame_bytes += b"\x00" * 100

    return frame_bytes


def test_audio_duration_seconds_valid_mp3() -> None:
    """Test audio_duration_seconds with valid MP3 data."""
    # Create a frame with 128 kbps, 44.1 kHz (should be ~0.026 seconds per frame)
    frame1 = _build_mp3_frame(bitrate_index=9, sample_rate_index=0)  # 128 kbps, 44.1 kHz
    frame2 = _build_mp3_frame(bitrate_index=9, sample_rate_index=0)  # Same settings
    mp3_data = frame1 + frame2

    duration = audio_duration_seconds(mp3_data)
    # Two frames at 44.1 kHz should be about 0.052 seconds (2 * 1152/44100)
    assert duration is not None
    assert abs(duration - 0.0522) < 0.001  # Allow small tolerance


def test_audio_duration_seconds_mp3_after_ogg_fails() -> None:
    """Test that MP3 parsing is tried when OGG parsing fails."""
    # Create MP3 data that doesn't look like OGG
    mp3_frame = _build_mp3_frame(bitrate_index=9, sample_rate_index=0)

    duration = audio_duration_seconds(mp3_frame)
    assert duration is not None
    assert duration > 0


def test_audio_duration_seconds_invalid_mp3() -> None:
    """Test audio_duration_seconds with invalid MP3 data."""
    # Random bytes that don't contain valid MP3 sync words
    invalid_data = b"this is not mp3 data at all"

    duration = audio_duration_seconds(invalid_data)
    assert duration is None


def test_audio_duration_seconds_mp3_too_short() -> None:
    """Test audio_duration_seconds with MP3 data too short."""
    short_data = b"FF"  # Less than 4 bytes

    duration = audio_duration_seconds(short_data)
    assert duration is None


def test_audio_duration_seconds_mp3_invalid_bitrate() -> None:
    """Test audio_duration_seconds with MP3 frame having invalid bitrate."""
    # Create frame with bitrate index 0 or 15 (invalid)
    invalid_frame = _build_mp3_frame(bitrate_index=0)  # Invalid bitrate

    duration = audio_duration_seconds(invalid_frame)
    assert duration is None


def test_audio_duration_seconds_mp3_invalid_sample_rate() -> None:
    """Test audio_duration_seconds with MP3 frame having invalid sample rate."""
    # Create frame with sample rate index 3 (invalid)
    invalid_frame = _build_mp3_frame(sample_rate_index=3)

    duration = audio_duration_seconds(invalid_frame)
    assert duration is None


def test_audio_duration_seconds_mp3_multiple_frames_different_bitrates() -> None:
    """Test audio_duration_seconds with multiple MP3 frames of different bitrates."""
    frame1 = _build_mp3_frame(bitrate_index=5)  # 64 kbps
    frame2 = _build_mp3_frame(bitrate_index=9)  # 128 kbps
    frame3 = _build_mp3_frame(bitrate_index=13)  # 256 kbps
    mp3_data = frame1 + frame2 + frame3

    duration = audio_duration_seconds(mp3_data)
    # Three frames should be about 0.078 seconds (3 * 1152/44100)
    assert duration is not None
    assert abs(duration - 0.0784) < 0.001
