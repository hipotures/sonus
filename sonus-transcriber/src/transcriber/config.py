import os
from typing import List, Tuple, Dict


# Define generated file extensions as constants
GENERATED_EXTENSIONS = ['.txt', '.tmp', '.err']
GENERATED_EXTENSIONS_TUPLE = tuple(GENERATED_EXTENSIONS)


# Environment variables with defaults
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
IS_CLOUD_RUN = bool(os.environ.get('K_SERVICE'))
PROJECT_ID = os.environ.get('PROJECT_ID', '')
WORK_DIR = os.environ.get('WORK_DIR', '/tmp/sonus/work')


def get_pubsub_config() -> Dict[str, str]:
    """Get Pub/Sub topic and subscription names.

    Returns:
        dict: Dictionary containing topic and subscription names

    Example:
        >>> get_pubsub_config()
        {
            'topic': 'sonus-pubsub-topic-test',
            'subscription': 'sonus-transcriber-sub-test'
        }
    """
    default_config = "sonus-pubsub-topic-test|sonus-transcriber-sub-test"
    config = os.environ.get("PUBSUB_CONFIG", default_config)

    if "|" not in config:
        raise ValueError(
            "Invalid PUBSUB_CONFIG format. Expected format: 'topic|subscription'")

    topic, subscription = config.split("|")

    if not topic or not subscription:
        raise ValueError("Empty topic or subscription in PUBSUB_CONFIG")

    return {
        "topic": topic,
        "subscription": subscription
    }


def get_supported_extensions() -> Tuple[List[str], List[str]]:
    """Get supported audio and video file extensions from environment variables.

    Returns:
        tuple: (audio_extensions, video_extensions) where each is a list of extensions
    """
    audio_extensions = os.environ.get(
        'AUDIO_EXTENSIONS', 'mp3,wav,m4a,flac').split(',')
    video_extensions = os.environ.get(
        'VIDEO_EXTENSIONS', 'mp4,mov,avi,mkv').split(',')
    return audio_extensions, video_extensions


def get_extensions_with_dot() -> Tuple[List[str], List[str]]:
    """Get supported audio and video file extensions with dot prefix.

    Returns:
        tuple: (audio_extensions_with_dot, video_extensions_with_dot)
    """
    audio_extensions, video_extensions = get_supported_extensions()
    audio_extensions_with_dot = [f".{ext}" for ext in audio_extensions]
    video_extensions_with_dot = [f".{ext}" for ext in video_extensions]
    return audio_extensions_with_dot, video_extensions_with_dot
