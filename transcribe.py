#!/usr/bin/env python3
"""
Video Transcription Tool - CLI Interface

Extracts English transcripts from videos using faster-whisper,
outputting JSON with timestamps. Optimized for 1-hour long videos.
"""

import argparse
import json
import sys
import os
import shutil
import tempfile
from pathlib import Path

from audio_extractor import extract_audio, get_audio_duration, AudioExtractionError
from transcriber import transcribe_audio, TranscriptionError
from config import SUPPORTED_FORMATS, MODEL_CONFIGS, DEFAULT_MODEL, DEFAULT_OUTPUT_DIR


def check_dependencies():
    """Check if required system dependencies are installed."""
    if not shutil.which("ffmpeg"):
        print("Error: ffmpeg is not installed or not in PATH")
        print("Please install ffmpeg:")
        print("  Ubuntu/Debian: sudo apt install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        sys.exit(1)


def validate_video_file(video_path: Path) -> None:
    """
    Validate that the video file exists and has a supported format.

    Args:
        video_path: Path to the video file

    Raises:
        SystemExit: If validation fails
    """
    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)

    if not video_path.is_file():
        print(f"Error: Path is not a file: {video_path}")
        sys.exit(1)

    if video_path.suffix.lower() not in SUPPORTED_FORMATS:
        print(f"Warning: File format {video_path.suffix} may not be supported")
        print(f"Supported formats: {', '.join(SUPPORTED_FORMATS)}")
        print("Attempting to process anyway...")
def validate_video_file(video_path: Path) -> None:
    """
    Validate that the video file exists and has a supported format.

    Args:
        video_path: Path to the video file

    Raises:
        SystemExit: If validation fails
    """
    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)

    if not video_path.is_file():
        print(f"Error: Path is not a file: {video_path}")
        sys.exit(1)

    if video_path.suffix.lower() not in SUPPORTED_FORMATS:
        print(f"Warning: File format {video_path.suffix} may not be supported")
        print(f"Supported formats: {', '.join(SUPPORTED_FORMATS)}")
        print("Attempting to process anyway...")


def get_output_path(video_path: Path, custom_output: str = None) -> Path:
    """
    Determine the output path for the transcript JSON file.

    Args:
        video_path: Path to the input video file
        custom_output: Custom output path if specified

    Returns:
        Path: Output path for the JSON file
    """
    if custom_output:
        return Path(custom_output)
    else:
        # Create output directory if it doesn't exist
        output_dir = Path(DEFAULT_OUTPUT_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate output filename
        output_filename = f"{video_path.stem}_transcript.json"
        return output_dir / output_filename


def format_time(seconds: float) -> str:
    """Format seconds into HH:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Transcribe video files to JSON with timestamps using faster-whisper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 transcribe.py video.mp4
  python3 transcribe.py video.mp4 --model tiny
  python3 transcribe.py video.mp4 -o custom_output.json
  python3 transcribe.py "WhatsApp Video 2026-01-19 at 6.28.12 PM.mp4"

Model sizes (base recommended for 1-hour videos):
  tiny   - Fastest, lower quality (~75MB download, ~1GB RAM)
  base   - Good balance (~150MB download, ~4GB RAM)
  small  - Better quality (~480MB download, ~5GB RAM)
  medium - High quality (~1.5GB download, ~8GB RAM)
  large  - Best quality (~3GB download, ~12GB RAM)
        """
    )

    parser.add_argument(
        "video_path",
        help="Path to the video file to transcribe"
    )

    parser.add_argument(
        "-m", "--model",
        default=DEFAULT_MODEL,
        choices=["tiny", "base", "small", "medium", "large"],
        help=f"Whisper model size (default: {DEFAULT_MODEL})"
    )

    parser.add_argument(
        "-o", "--output",
        help="Custom output path for JSON file (default: output/<video_name>_transcript.json)"
    )

    args = parser.parse_args()

    # Check system dependencies
    check_dependencies()

    # Validate and prepare paths
    video_path = Path(args.video_path)
    validate_video_file(video_path)

    output_path = get_output_path(video_path, args.output)

    # Create parent directory for output if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Video Transcription Tool")
    print("=" * 60)
    print(f"Input video: {video_path}")
    print(f"Model: {args.model}")
    print(f"Output: {output_path}")
    print("=" * 60)

    # Get video duration for user info
    duration = get_audio_duration(str(video_path))
    if duration > 0:
        print(f"Video duration: {format_time(duration)}")

    # Create temporary file for audio extraction
    temp_audio_path = None

    try:
        # Create temporary WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            temp_audio_path = tmp.name

        # Step 1: Extract audio
        print("\n[1/3] Extracting audio from video...")
        extract_audio(str(video_path), temp_audio_path)
        print("Audio extraction complete!")

        # Step 2: Transcribe
        print(f"\n[2/3] Transcribing with {args.model} model...")
        results = transcribe_audio(temp_audio_path, args.model)

        if not results:
            print("Warning: No speech detected in the video")
            results = []

        # Step 3: Save results
        print("\n[3/3] Saving transcription to JSON...")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        # Print summary
        print("\n" + "=" * 60)
        print("Transcription Complete!")
        print("=" * 60)
        print(f"Output file: {output_path}")
        print(f"Total segments: {len(results)}")

        if results:
            total_duration = results[-1]["end_time"] if results else 0
            print(f"Transcribed duration: {format_time(total_duration)}")

            # Show first segment as preview
            print(f"\nFirst segment preview:")
            print(f"  [{results[0]['start_time']:.2f}s - {results[0]['end_time']:.2f}s]")
            preview_text = results[0]['text'][:100]
            if len(results[0]['text']) > 100:
                preview_text += "..."
            print(f"  {preview_text}")

        print("=" * 60)

    except AudioExtractionError as e:
        print(f"\nError during audio extraction: {e}", file=sys.stderr)
        sys.exit(1)

    except TranscriptionError as e:
        print(f"\nError during transcription: {e}", file=sys.stderr)
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nTranscription interrupted by user", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"\nUnexpected error: {e}", file=sys.stderr)
        sys.exit(1)

    finally:
        # Cleanup temporary audio file
        if temp_audio_path and os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
                print("\nTemporary files cleaned up")
            except Exception as e:
                print(f"\nWarning: Could not remove temporary file: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
