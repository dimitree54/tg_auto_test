"""MP3 duration extraction helper."""

import struct


def parse_mp3_duration(data: bytes) -> float | None:
    """Parse MP3 format and return duration in seconds."""
    if len(data) < 4:
        return None

    # MPEG1 Layer 3 bitrate table (kbps)
    bitrates = [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0]

    # MPEG1 sample rate table (Hz)
    sample_rates = [44100, 48000, 32000, 0]

    total_duration = 0.0
    offset = 0
    data_len = len(data)

    while offset + 4 <= data_len:
        # Find sync word (11 bits set to 1)
        if data[offset] != 0xFF or (data[offset + 1] & 0xE0) != 0xE0:
            offset += 1
            continue

        # Parse frame header
        header = struct.unpack(">I", data[offset : offset + 4])[0]

        # Check MPEG version (bits 20-19: 11 = MPEG1, 10 = MPEG2, 01 = MPEG2.5)
        version = (header >> 19) & 0x03
        if version != 0x03:  # Only MPEG1 for simplicity
            offset += 1
            continue

        # Check layer (bits 18-17: 01 = Layer III)
        layer = (header >> 17) & 0x03
        if layer != 0x01:
            offset += 1
            continue

        # Extract bitrate index (bits 15-12)
        bitrate_index = (header >> 12) & 0x0F
        if bitrate_index == 0 or bitrate_index == 15:
            offset += 1
            continue

        # Extract sample rate index (bits 11-10)
        sample_rate_index = (header >> 10) & 0x03
        if sample_rate_index == 3:
            offset += 1
            continue

        # Calculate frame parameters
        bitrate = bitrates[bitrate_index] * 1000  # Convert to bps
        sample_rate = sample_rates[sample_rate_index]
        padding = (header >> 9) & 0x01

        # Calculate frame length and duration
        frame_length = (144 * bitrate) // sample_rate + padding
        frame_duration = 1152.0 / sample_rate  # 1152 samples per MP3 frame

        total_duration += frame_duration
        offset += frame_length

        # Safety check to prevent infinite loops
        if frame_length <= 0:
            break

    return total_duration if total_duration > 0 else None
