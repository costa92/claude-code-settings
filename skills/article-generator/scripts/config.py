#!/usr/bin/env python3
"""
Shared configuration constants for article-generator skill
"""

import os
import json
from pathlib import Path
from typing import Dict, Any


def load_user_config(config_path: str = "~/.article-generator.conf") -> Dict[str, Any]:
    """
    Load user configuration from file

    Args:
        config_path: Path to user config file

    Returns:
        dict: User configuration or empty dict if not found
    """
    config_file = Path(config_path).expanduser()

    if not config_file.exists():
        return {}

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


# Load user configuration
_user_config = load_user_config()

# Aspect ratio to resolution mapping
# NOTE: Only these aspect ratios are supported by Gemini API
ASPECT_RATIO_MAP = {
    "1024x1024": "1:1",  # 1:1
    "832x1248": "2:3",  # 2:3
    "1248x832": "3:2",  # 3:2
    "864x1184": "3:4",  # 3:4
    "1184x864": "4:3",  # 4:3
    "896x1152": "4:5",  # 4:5
    "1152x896": "5:4",  # 5:4
    "768x1344": "9:16",  # 9:16
    "1344x768": "16:9",  # 16:9 - Use this for WeChat covers, then crop to 900x383
    "1536x672": "21:9",  # 21:9
}

# Reverse mapping: aspect ratio string -> size string
ASPECT_RATIO_TO_SIZE = {
    "1:1": "1024x1024",
    "2:3": "832x1248",
    "3:2": "1248x832",  # STANDARDIZED: 3:2 aspect ratio
    "3:4": "864x1184",
    "4:3": "1184x864",
    "4:5": "896x1152",
    "5:4": "1152x896",
    "9:16": "768x1344",
    "16:9": "1344x768",
    "21:9": "1536x672",
}

# Timeout configurations (in seconds)
# User config can override these via ~/.article-generator.conf
_default_timeouts = {
    "image_generation": 120,  # 2 minutes per image
    "upload": 60,  # 1 minute for upload
    "dependency_check": 5,  # 5 seconds for version checks
    "npm_install": 120,  # 2 minutes for npm install
}

# Merge user config with defaults (user config takes precedence)
TIMEOUTS = {**_default_timeouts, **_user_config.get("timeouts", {})}

# Retry configurations
RETRY_CONFIG = {
    "max_attempts": 3,
    "initial_delay": 2,  # seconds
    "backoff_factor": 1.5,  # exponential backoff multiplier
    "retriable_errors": [
        "SSL",
        "ConnectionError",
        "TimeoutError",
        "NetworkError",
        "500",  # Server errors
        "502",
        "503",
        "504",
    ]
}

# Image generation defaults
IMAGE_DEFAULTS = {
    "resolution": "2K",  # 1K, 2K, or 4K
    "model": "gemini-3-pro-image-preview",
    "cover_aspect_ratio": "16:9",  # 1344x768, crop to 900x383 for WeChat
    "rhythm_aspect_ratio": "3:2",  # 1248x832 for article body images
}

# PicGo configuration
PICGO_CONFIG = {
    "command": "picgo",
    "upload_timeout": 60,
}
