# Video Transcription Tool

A Python CLI tool to extract English transcripts from videos using faster-whisper, outputting JSON with timestamps. Optimized for 1-hour long videos with completely free, local processing.

## Features

- Extract transcripts from video files (mp4, avi, mkv, mov, etc.)
- Generate JSON output with timestamped segments
- Free and local processing (no API costs)
- Optimized for 1-hour long videos
- Multiple model sizes for speed/quality tradeoff
- Voice Activity Detection (VAD) to skip silence
- Automatic cleanup of temporary files

## Requirements

### System Requirements
- Python 3.8 or higher
- ffmpeg (must be installed system-wide)
- 4-5GB RAM (for base model)
- ~300MB disk space (for model download on first run)

### System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html and add to PATH

## Installation

1. Clone or navigate to this directory:
```bash
cd video_to_transcript_cli_tool
```

2. Install Python dependencies:
```bash
pip3 install -r requirements.txt
```

On first run, the selected model will be automatically downloaded (~150MB for base model).

## Usage

### Basic Usage

```bash
python3 transcribe.py "video.mp4"
```

This will:
1. Extract audio from the video
2. Transcribe using the base model (default)
3. Save output to `output/video_transcript.json`

### Usage Examples

```bash
# Transcribe with default settings
python3 transcribe.py "WhatsApp Video 2026-01-19 at 6.28.12 PM.mp4"

# Use faster tiny model (lower quality but quicker)
python3 transcribe.py video.mp4 --model tiny

# Use better quality small model
python3 transcribe.py video.mp4 --model small

# Custom output location
python3 transcribe.py video.mp4 -o /path/to/output.json

# Combine options
python3 transcribe.py long_video.mp4 --model base -o transcript.json
```

## Model Selection

Choose the model based on your needs:

| Model  | Speed    | Quality | RAM   | Download | Best For |
|--------|----------|---------|-------|----------|----------|
| tiny   | Fastest  | Lower   | ~1GB  | ~75MB    | Quick tests, drafts |
| base   | Fast     | Good    | ~4GB  | ~150MB   | **Recommended for 1-hour videos** |
| small  | Medium   | Better  | ~5GB  | ~480MB   | Better accuracy needed |
| medium | Slow     | High    | ~8GB  | ~1.5GB   | Professional use |
| large  | Slowest  | Best    | ~12GB | ~3GB     | Maximum accuracy |

**Recommendation:** Use `base` model for the best balance of speed and quality for 1-hour videos.

## Output Format

The tool generates a JSON file with the following structure:

```json
[
  {
    "text": "This is the first segment of transcribed speech.",
    "start_time": 0.0,
    "end_time": 3.5
  },
  {
    "text": "This is the second segment.",
    "start_time": 3.5,
    "end_time": 7.2
  }
]
```

Each segment contains:
- `text`: The transcribed text
- `start_time`: Start timestamp in seconds (float)
- `end_time`: End timestamp in seconds (float)

## Performance

### Expected Performance (1-hour video, base model, CPU)

- **Processing time**: 6-10 minutes
- **Peak RAM usage**: ~4-5 GB
- **Temporary disk usage**: ~115 MB (automatically cleaned up)
- **Output JSON size**: ~50-200 KB (depending on speech density)

### Optimizations

The tool includes several optimizations for long videos:

1. **int8 Quantization**: 75% memory reduction with minimal accuracy loss
2. **VAD Filtering**: Skips silence, resulting in 20-40% speed improvement
3. **Efficient Streaming**: Processes audio in chunks without loading entire file into memory
4. **Automatic Cleanup**: Removes temporary files after processing

## Command-Line Options

```
usage: transcribe.py [-h] [-m {tiny,base,small,medium,large}] [-o OUTPUT] video_path

positional arguments:
  video_path            Path to the video file to transcribe

optional arguments:
  -h, --help            Show this help message and exit
  -m {tiny,base,small,medium,large}, --model {tiny,base,small,medium,large}
                        Whisper model size (default: base)
  -o OUTPUT, --output OUTPUT
                        Custom output path for JSON file
                        (default: output/<video_name>_transcript.json)
```

## Supported Video Formats

- MP4 (.mp4)
- AVI (.avi)
- MKV (.mkv)
- MOV (.mov)
- FLV (.flv)
- WMV (.wmv)
- WebM (.webm)

The tool uses ffmpeg for audio extraction, so any format supported by ffmpeg should work.

## Troubleshooting

### "Error: ffmpeg is not installed or not in PATH"

Install ffmpeg using your system's package manager (see Installation section above).

### "Transcription failed: out of memory"

Try using a smaller model:
```bash
python3 transcribe.py video.mp4 --model tiny
```

### "No speech detected in the video"

The video may have:
- No audio track
- Only music/background noise
- Very low volume

Check the video file to ensure it contains speech.

### Slow processing

For faster processing:
1. Use a smaller model (`--model tiny`)
2. If you have an NVIDIA GPU, you can modify `transcriber.py` to use `device="cuda"` instead of `device="cpu"`

### First run downloads model files

This is expected behavior. The model is downloaded once and cached for future use. The download size depends on the model:
- tiny: ~75MB
- base: ~150MB
- small: ~480MB

## Project Structure

```
transctipt_from_video/
├── transcribe.py          # Main CLI entry point
├── transcriber.py         # Transcription logic (faster-whisper)
├── audio_extractor.py     # Audio extraction from video
├── config.py              # Configuration constants
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── .gitignore             # Git ignore rules
└── output/                # Generated transcripts (auto-created)
```

## Technical Details

### Audio Processing

Videos are converted to:
- Format: WAV (PCM 16-bit)
- Sample rate: 16kHz
- Channels: Mono (1 channel)

This format is optimized for Whisper's requirements.

### Transcription Engine

Uses **faster-whisper**, an optimized implementation of OpenAI's Whisper:
- 4x faster than standard Whisper
- Lower memory usage
- Based on CTranslate2
- Same accuracy as original Whisper

## License

This tool uses:
- **faster-whisper**: MIT License
- **ffmpeg-python**: Apache License 2.0
- **ffmpeg**: GPL/LGPL (system dependency)

## Credits

Built with:
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Efficient Whisper implementation
- [ffmpeg-python](https://github.com/kkroening/ffmpeg-python) - Python bindings for FFmpeg
- [OpenAI Whisper](https://github.com/openai/whisper) - Original speech recognition model
