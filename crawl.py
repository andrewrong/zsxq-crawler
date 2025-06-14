#!/usr/bin/env python3
"""
知识星球 content crawler
Supports real-time Telegram notifications
"""
import os
import time
from datetime import datetime

from config import validate_config, GROUP_CONFIG_MANAGER
from src.crawlers.zsxq_crawler import ZsxqCrawler
from src.formatters.message_formatter import TelegramFormatter
from src.notifiers.telegram_notifier import TelegramNotifier
from src.utils.group_config import GroupConfig
from src.utils.logger import setup_logger
from src.managers.group_manager import GroupManager
from state_manager import CrawlType, StateManager

logger = setup_logger(__name__)

def process_topics(crawler, notifier, topics, crawl_type, thread_id):
    """Process topics: format and send to Telegram"""
    success_count = 0
    last_topic_id = None
    
    # Process topics from oldest to newest
    reversed_topics = list(reversed(topics))
    for topic in reversed_topics:
        try:
            # Format and send
            message = TelegramFormatter.format_topic(topic, crawl_type)
            notifier.send_message_sync(
                text=message,
                thread_id=thread_id,
                images=topic.talk.images if topic.talk else None,
                files=topic.talk.files if topic.talk else None,
                parse_mode='HTML'
            )
            success_count += 1
            logger.info(f"Sent topic: {topic.title or f'ID:{topic.topic_id}'}")
            
            # Record last processed topic ID
            if not last_topic_id or topic.topic_id > last_topic_id:
                last_topic_id = topic.topic_id
                
            time.sleep(2)  # Avoid sending too fast
            
        except Exception as e:
            logger.error(f"Failed to process topic [ID:{topic.topic_id}]: {e}")
            continue
            
    return success_count, last_topic_id


def process_group(group_config: GroupConfig, notifier: TelegramNotifier):
    """Process a single group"""
    group_id = group_config.get_group_id()
    group_manager = GroupManager()
    group_name = group_manager.get_group_name(group_id)
    logger.info(f"Processing group: {group_name}")
    
    # Initialize crawler for this group
    crawler = ZsxqCrawler(group_id)
    
    # Process home topics if enabled
    if group_config.get_is_crawl_home():
        home_state = StateManager.get_state(group_id, CrawlType.HOME)
        last_home_id = home_state.get('last_topic_id') if home_state else None
        
        topics, new_last_topic_id = crawler.crawl_home_topics(last_topic_id=last_home_id)
        if topics:
            thread_id = group_config.get_thread_id('home')
            success_count, last_topic_id = process_topics(crawler, notifier, topics, CrawlType.HOME.value, thread_id)
            if success_count > 0:
                StateManager.save_state(group_id, CrawlType.HOME, {
                    'last_topic_id': last_topic_id,
                    'update_time': datetime.now().isoformat()
                })
                logger.info(f"Successfully forwarded {success_count} home updates for group {group_name}")
        else:
            logger.info(f"No new home content for group {group_name}")
    
    # Process digest topics
    digest_state = StateManager.get_state(group_id, CrawlType.DIGEST)
    last_digest_id = digest_state.get('last_topic_id') if digest_state else None
    
    digest_topics, new_last_digest_id = crawler.get_digest_topics(last_topic_id=last_digest_id)
    if digest_topics:
        thread_id = group_config.get_thread_id('digest')
        success_count, last_topic_id = process_topics(crawler, notifier, digest_topics, CrawlType.DIGEST.value, thread_id)
        if success_count > 0:
            StateManager.save_state(group_id, CrawlType.DIGEST, {
                'last_topic_id': last_topic_id,
                'update_time': datetime.now().isoformat()
            })
            logger.info(f"Successfully forwarded {success_count} digest updates for group {group_name}")
    else:
        logger.info(f"No new digest content for group {group_name}")


def main():
    # Validate environment variables
    try:
        validate_config()
    except ValueError as e:
        logger.error(f"Configuration error: {str(e)}")
        return

    # Initialize group manager and load group info
    group_manager = GroupManager()
    if not group_manager.initialize_groups():
        logger.error("Failed to initialize groups, exiting...")
        return

    # Initialize notifier
    notifier = TelegramNotifier()
    
    try:
        logger.info("Starting to crawl 知识星球 content...")
        
        # Process each configured group
        for group_id in GROUP_CONFIG_MANAGER.get_group_configs():
            group_config = GROUP_CONFIG_MANAGER.get_group_config(group_id)
            if group_config:
                process_group(group_config, notifier)
            
    except Exception as e:
        logger.error(f"Error during crawling: {str(e)}")
        return
    finally:
        group_manager.close()


if __name__ == "__main__":
    main()