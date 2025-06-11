"""
Configuration settings for the 知识星球 crawler.
"""
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from src.utils.group_config import GroupConfigManager

def get_env_or_default(key: str, default: str = None) -> Optional[str]:
    """Get environment variable with default value"""
    return os.getenv(key, default)

# 知识星球 settings - from environment variables
COOKIE = get_env_or_default('ZSXQ_COOKIE')

# Group configurations
groups_config = get_env_or_default('ZSXQ_GROUPS', '{}')  # Default to empty JSON object
# Initialize group config manager
GROUP_CONFIG_MANAGER = GroupConfigManager(groups_config)

# Crawling settings
MAX_TOPICS_PER_FETCH = 20
CRAWL_INTERVAL_MINUTES = int(get_env_or_default('CRAWL_INTERVAL_MINUTES', '60'))  # Default to 60 minutes
TEMP_DIR = Path(get_env_or_default('TEMP_DIR',  '/tmp/zsxq_downloads'))
os.makedirs(TEMP_DIR, exist_ok=True)

# Telegram settings - from environment variables
TELEGRAM_BOT_TOKEN = get_env_or_default('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = get_env_or_default('TELEGRAM_CHAT_ID')
TELEGRAM_TOPIC_ERROR_ID = get_env_or_default('TELEGRAM_TOPIC_ERROR_ID', None)

# State persistence
LAST_CRAWLED_FILE = 'last_crawled.json'


def validate_config():
    """Validate required environment variables"""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is required")
    if not TELEGRAM_CHAT_ID:
        raise ValueError("TELEGRAM_CHAT_ID is required")
    if not COOKIE:
        raise ValueError("ZSXQ_COOKIE is required")
    if GROUP_CONFIG_MANAGER.is_empty():
        raise ValueError("At least one group configuration is required in ZSXQ_GROUPS")
