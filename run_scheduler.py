#!/usr/bin/env python3
"""
知识星球 content crawler scheduler
Runs periodic crawls and sends updates to Telegram
"""
import logging
from config import validate_config, GROUP_CONFIG_MANAGER, CRAWL_INTERVAL_MINUTES
from src.scheduler.crawl_scheduler import CrawlScheduler
from src.utils.logger import setup_logger

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = setup_logger(__name__)

def main():
    # Validate environment variables
    try:
        validate_config()
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        return

    try:
        # Initialize and start scheduler
        scheduler = CrawlScheduler(GROUP_CONFIG_MANAGER)
        scheduler.start(CRAWL_INTERVAL_MINUTES)
        
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")
        return

if __name__ == "__main__":
    main() 