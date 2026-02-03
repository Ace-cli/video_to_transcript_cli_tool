"""Audio extraction module for converting video to audio format suitable for transcription."""

import ffmpeg
import os
from pathlib import Path
from config import AUDIO_SAMPLE_RATE, AUDIO_CHANNELS, AUDIO_CODEC


class AudioExtractionError(Exception):
    """Exception raised when audio extraction fails."""
    pass


def extract_audio(video_path: str, output_path: str) -> str:
    """
    Extract audio from video file and convert to WAV format for Whisper.

    Args:
        video_path: Path to the input video file
        output_path: Path where the extracted audio should be saved

    Returns:
        str: Path to the extracted audio file

    Raises:
        AudioExtractionError: If extraction fails
        FileNotFoundError: If video file doesn't exist
    """
    # Validate input file exists
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    try:
        # Extract audio using ffmpeg
        # Convert to 16kHz mono WAV with 16-bit PCM encoding (Whisper requirements)
        stream = ffmpeg.input(video_path)
        stream = ffmpeg.output(
            stream,
            output_path,
            acodec=AUDIO_CODEC,      # 16-bit PCM
            ac=AUDIO_CHANNELS,       # Mono (1 channel)
            ar=str(AUDIO_SAMPLE_RATE)  # 16kHz sample rate
        )

        # Run ffmpeg with error suppression for clean output
        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

        return output_path

    except ffmpeg.Error as e:
        # Decode error message from stderr
        error_message = e.stderr.decode() if e.stderr else str(e)
        raise AudioExtractionError(f"Failed to extract audio: {error_message}")
    except Exception as e:
        raise AudioExtractionError(f"Unexpected error during audio extraction: {str(e)}")


def get_audio_duration(video_path: str) -> float:
    """
    Get the duration of the video/audio in seconds.

    Args:
        video_path: Path to the video file

    Returns:
        float: Duration in seconds
    """
    try:
        probe = ffmpeg.probe(video_path)
        duration = float(probe['format']['duration'])
        return duration
    except Exception:
        return 0.0
