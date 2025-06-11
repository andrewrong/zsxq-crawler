import time
import logging
from datetime import datetime
from typing import Optional

from src.crawlers.zsxq_crawler import ZsxqCrawler
from src.notifiers.telegram_notifier import TelegramNotifier
from src.utils.group_config import GroupConfigManager, GroupConfig
from state_manager import CrawlType, StateManager
from src.formatters.message_formatter import TelegramFormatter
from src.managers.group_manager import GroupManager
from src.utils.logger import setup_logger
from config import CRAWL_INTERVAL_MINUTES, TELEGRAM_TOPIC_ERROR_ID


logger = setup_logger(__name__)

class CrawlScheduler:
    def __init__(self, group_config_manager: GroupConfigManager):
        self.group_config_manager = group_config_manager
        self.notifier = TelegramNotifier()
        self.group_manager = GroupManager()
        self.running = False
        
    def crawl_job(self):
        """Main crawl job that processes all groups"""
        logger.info(f"Starting scheduled crawl job at {datetime.now()}")
        try:
            for group_id in self.group_config_manager.get_group_configs():
                group_config = self.group_config_manager.get_group_config(group_id)
                if group_config:
                    self._process_group(group_config)
        except Exception as e:
            logger.error(f"Error in crawl job: {str(e)}")
            self.notifier.send_message_sync(
                text=f"❌ Crawl job failed: {str(e)}",
                thread_id=TELEGRAM_TOPIC_ERROR_ID,
                parse_mode='HTML'
            )
            
    def _process_group(self, group_config):
        """Process a single group"""
        group_id = group_config.get_group_id()
        group_name = self.group_manager.get_group_name(group_id)
        logger.info(f"Processing group: {group_name}")
        
        try:
            crawler = ZsxqCrawler(group_id)
            
            # Process home topics if enabled
            if group_config.get_is_crawl_home():
                self._process_home_topics(crawler, group_config)
            
            # Process digest topics
            self._process_digest_topics(crawler, group_config)
            
        except Exception as e:
            logger.error(f"Error processing group {group_name}: {str(e)}")
            self.notifier.send_message_sync(
                text=f"❌ Error processing group {group_name}: {str(e)}",
                thread_id=TELEGRAM_TOPIC_ERROR_ID,
                parse_mode='HTML'
            )
            
    def _process_home_topics(self, crawler, group_config):
        """Process home topics for a group"""
        group_id = group_config.get_group_id()
        group_name = self.group_manager.get_group_name(group_id)
        home_state = StateManager.get_state(group_id, CrawlType.HOME)
        last_home_id = home_state.get('last_topic_id') if home_state else None
        
        topics, new_last_topic_id = crawler.crawl_home_topics(last_topic_id=last_home_id)
        if topics:
            thread_id = group_config.get_thread_id('home')
            success_count, last_topic_id = self._process_topics(
                crawler, topics, CrawlType.HOME.value, thread_id
            )
            if success_count > 0:
                StateManager.save_state(group_id, CrawlType.HOME, {
                    'last_topic_id': last_topic_id,
                    'update_time': datetime.now().isoformat()
                })
                logger.info(f"Successfully forwarded {success_count} home updates for group {group_name}")
        else:
            logger.info(f"No new home content for group {group_name}")
            
    def _process_digest_topics(self, crawler: ZsxqCrawler, group_config: GroupConfig):
        """Process digest topics for a group"""
        group_id = group_config.get_group_id()
        group_name = self.group_manager.get_group_name(group_id)
        digest_state = StateManager.get_state(group_id, CrawlType.DIGEST)
        last_digest_id = digest_state.get('last_topic_id') if digest_state else None
        
        digest_topics, new_last_digest_id = crawler.get_digest_topics(last_topic_id=last_digest_id)
        if digest_topics:
            thread_id = group_config.get_thread_id('digest')
            success_count, last_topic_id = self._process_topics(
                crawler, digest_topics, CrawlType.DIGEST.value, thread_id
            )
            if success_count > 0:
                StateManager.save_state(group_id, CrawlType.DIGEST, {
                    'last_topic_id': last_topic_id,
                    'update_time': datetime.now().isoformat()
                })
                logger.info(f"Successfully forwarded {success_count} digest updates for group {group_name}")
        else:
            logger.info(f"No new digest content for group {group_name}")
            
    def _process_topics(self, crawler, topics, crawl_type, thread_id):
        """Process topics: format and send to Telegram"""
        success_count = 0
        last_topic_id = None
        
        # Process topics from oldest to newest
        reversed_topics = list(reversed(topics))
        for topic in reversed_topics:
            try:
                # Format and send
                message = TelegramFormatter.format_topic(topic, crawl_type)
                self.notifier.send_message_with_media(
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
        
    def start(self, interval_minutes: int = 60):
        """Start the scheduler with the specified interval"""
        logger.info(f"Starting scheduler with {interval_minutes} minute interval")
        self.running = True
        
        # Run immediately on start
        self.crawl_job()
        
        # Keep the scheduler running
        while self.running:
            try:
                # Sleep for the specified interval
                time.sleep(interval_minutes * 60)
                
                # Run the crawl job
                self.crawl_job()
                
            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                time.sleep(60)  # Wait a minute before retrying
                
    def stop(self):
        """Stop the scheduler"""
        logger.info("Stopping scheduler")
        self.running = False 