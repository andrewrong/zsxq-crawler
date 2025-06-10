"""
Configuration settings for the 知识星球 crawler.
"""
import os
from typing import Dict, List, Optional, Any
from src.utils.group_config import GroupConfigManager

def get_env_or_default(key: str, default: str = None) -> Optional[str]:
    """Get environment variable or return default value"""
    return os.environ.get(key, default)

# 知识星球 settings - from environment variables
COOKIE = get_env_or_default('ZSXQ_COOKIE')

# Group configurations
groups_config = get_env_or_default('ZSXQ_GROUPS', '{}')  # Default to empty JSON object
# Initialize group config manager
GROUP_CONFIG_MANAGER = GroupConfigManager(groups_config)

# Crawling settings
MAX_TOPICS_PER_FETCH = 20

# Telegram settings - from environment variables
TELEGRAM_BOT_TOKEN = get_env_or_default('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = get_env_or_default('TELEGRAM_CHAT_ID')
TELEGRAM_TOPIC_ID = get_env_or_default('TELEGRAM_TOPIC_ID', None)

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
