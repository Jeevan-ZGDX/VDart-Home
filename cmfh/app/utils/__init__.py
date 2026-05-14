"""Utilities module for CMFH"""

import os
from pathlib import Path


def get_data_dir() -> Path:
    """Get data directory"""
    data_dir = Path(__file__).parent.parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


def get_models_dir() -> Path:
    """Get models directory"""
    models_dir = Path(__file__).parent.parent.parent / "models"
    models_dir.mkdir(exist_ok=True)
    return models_dir


def ensure_directories():
    """Ensure all required directories exist"""
    dirs = [
        get_data_dir(),
        get_models_dir(),
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def get_config() -> dict:
    """Get configuration"""
    return {
        "whisper_model": os.getenv("WHISPER_MODEL", "tiny"),
        "ollama_url": os.getenv("OLLAMA_URL", "http://localhost:11434"),
        "ollama_model": os.getenv("OLLAMA_MODEL", "phi3"),
        "sample_rate": int(os.getenv("SAMPLE_RATE", "16000")),
        "chunk_duration": float(os.getenv("CHUNK_DURATION", "10.0")),
    }