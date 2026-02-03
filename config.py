"""Configuration constants for video transcription tool."""

# Supported video formats
SUPPORTED_FORMATS = ['.mp4', '.avi', '.mkv', '.mov', '.flv', '.wmv', '.webm']

# Audio extraction settings
AUDIO_SAMPLE_RATE = 16000  # 16kHz required by Whisper
AUDIO_CHANNELS = 1  # Mono
AUDIO_CODEC = 'pcm_s16le'  # 16-bit PCM

# Model configurations
MODEL_CONFIGS = {
    "tiny": {
        "params": "39M",
        "ram_gb": 1,
        "speed": "fastest",
        "download_mb": 75
    },
    "base": {
        "params": "74M",
        "ram_gb": 4,
        "speed": "fast",
        "download_mb": 150
    },
    "small": {
        "params": "244M",
        "ram_gb": 5,
        "speed": "medium",
        "download_mb": 480
    },
    "medium": {
        "params": "769M",
        "ram_gb": 8,
        "speed": "slow",
        "download_mb": 1500
    },
    "large": {
        "params": "1550M",
        "ram_gb": 12,
        "speed": "slowest",
        "download_mb": 3000
    }
}

# Default model for transcription
DEFAULT_MODEL = "base"

# Output directory
DEFAULT_OUTPUT_DIR = "output"
