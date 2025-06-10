"""
Configuration settings for the 知识星球 crawler
Environment variables:
    ZSXQ_COOKIE: 知识星球 cookie
    ZSXQ_GROUP_ID: 知识星球 group ID
    TELEGRAM_BOT_TOKEN: Telegram bot token
    TELEGRAM_CHAT_ID: Telegram chat ID
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)


def get_env_or_default(key, default=''):
    """Get value from environment variable or return default value"""
    return os.environ.get(key, default)

# 知识星球 settings - from environment variables
COOKIE = get_env_or_default('ZSXQ_COOKIE')
ZSXQ_GROUP_ID = get_env_or_default('ZSXQ_GROUP_ID')

# Crawling settings
MAX_TOPICS_PER_FETCH = 20

# 是否采集home
IS_CRAWL_HOME = get_env_or_default('IS_CRAWL_HOME', 'true').lower() == 'true'

# Telegram settings - from environment variables
TELEGRAM_BOT_TOKEN = get_env_or_default('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = get_env_or_default('TELEGRAM_CHAT_ID')
TELEGRAM_TOPIC_ID = get_env_or_default('TELEGRAM_TOPIC_ID', None)

# State persistence
LAST_CRAWLED_FILE = 'last_crawled.json'

# Validate required environment variables
def validate_config():
    """Validate that all required environment variables are set"""
    required_vars = {
        'ZSXQ_COOKIE': COOKIE,
        'ZSXQ_GROUP_ID': ZSXQ_GROUP_ID,
        'TELEGRAM_BOT_TOKEN': TELEGRAM_BOT_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID
    }
    
    missing_vars = [key for key, value in required_vars.items() if not value]
    
    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            "Please set these variables in your environment before running the script."
        )
