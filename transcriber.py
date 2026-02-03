"""Transcription module using faster-whisper for efficient speech-to-text conversion."""

from faster_whisper import WhisperModel
from typing import List, Dict
import os


class TranscriptionError(Exception):
    """Exception raised when transcription fails."""
    pass


def transcribe_audio(audio_path: str, model_size: str = "base") -> List[Dict]:
    """
    Transcribe audio file using faster-whisper with optimizations for long videos.

    Args:
        audio_path: Path to the audio file (WAV format, 16kHz mono)
        model_size: Whisper model size (tiny/base/small/medium/large)

    Returns:
        List[Dict]: List of transcription segments with text and timestamps
            Each dict contains:
            - text: Transcribed text
            - start_time: Start timestamp in seconds
            - end_time: End timestamp in seconds

    Raises:
        TranscriptionError: If transcription fails
        FileNotFoundError: If audio file doesn't exist
    """
    # Validate input file
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    try:
        print(f"Loading {model_size} model (this may take a moment on first run)...")

        # Initialize model with optimizations for 1-hour videos
        # - device="cpu": Use CPU processing (change to "cuda" for GPU)
        # - compute_type="int8": 75% memory reduction with minimal accuracy loss
        model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8"
        )

        print("Transcribing audio (this may take several minutes for long videos)...")

        # Transcribe with optimizations
        segments, info = model.transcribe(
            audio_path,
            language="en",  # Force English transcription
            beam_size=5,  # Balance between speed and quality (1=fastest, 5=better quality)
            vad_filter=True,  # Voice Activity Detection - skips silence
            vad_parameters=dict(
                min_silence_duration_ms=500,  # Minimum silence duration to skip
                threshold=0.5  # Voice activity threshold
            ),
            condition_on_previous_text=True  # Use previous text for context
        )

        print(f"Detected language: {info.language} (probability: {info.language_probability:.2f})")
        print(f"Processing segments...")

        # Convert generator to list of dictionaries
        results = []
        for segment in segments:
            results.append({
                "text": segment.text.strip(),
                "start_time": round(segment.start, 2),
                "end_time": round(segment.end, 2)
            })

        return results

    except Exception as e:
        raise TranscriptionError(f"Transcription failed: {str(e)}")


def transcribe_audio_with_progress(audio_path: str, model_size: str = "base") -> List[Dict]:
    """
    Transcribe audio with progress indication.

    This is a wrapper around transcribe_audio that could be extended
    to show progress bars for very long videos.

    Args:
        audio_path: Path to the audio file
        model_size: Whisper model size

    Returns:
        List[Dict]: Transcription results
    """
    return transcribe_audio(audio_path, model_size)
