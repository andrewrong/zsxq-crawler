"""
知识星球 content crawler implementation
"""
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse
import os

import requests

from config import COOKIE, GROUP_CONFIG_MANAGER

from .models import Topic, SimpleTopic
from src.utils.logger import setup_logger
from src.managers.group_manager import GroupManager

logger = setup_logger(__name__)


class ZsxqCrawler:
    def __init__(self, group_id: str):
        """
        Initialize crawler for a specific group
        
        Args:
            group_id: Group ID to crawl
        """
        self.headers = {
            'Cookie': "zsxq_access_token=" + COOKIE,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.group_id = group_id
        self.group_name = GroupManager().get_group_name(group_id)
        self.base_url = 'https://api.zsxq.com/v2'
        
    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send API request and return JSON response"""
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    def get_topic_detail(self, topic_id: str) -> Optional[Topic]:
        """Get detailed information for a single topic"""
        url = f"{self.base_url}/topics/{topic_id}/info"
        try:
            data = self._make_request(url)
            if data.get('succeeded'):
                topic_data = data['resp_data']['topic']
                return Topic.from_dict(topic_data)
        except Exception as e:
            logger.error(f"Failed to get topic detail (ID: {topic_id}): {e}")
        return None

    def get_digest_topics(self, count: int = 30, sort: str = 'by_create_time', direction: str = 'desc', last_topic_id: Optional[str] = None) -> Tuple[List[Topic], Optional[str]]:
        """
        Get digest topics list
        
        Args:
            count: Number of topics to fetch per request
            sort: Sort method ('by_create_time')
            direction: Sort direction ('desc' or 'asc')
            last_topic_id: Last crawled topic ID
            
        Returns:
            tuple: (topics, last_topic_id)
        """
        url = f"{self.base_url}/groups/{self.group_id}/topics/digests"
        all_topics = []
        found_last_topic = False
        next_index = None
        
        while True:
            try:
                params = {
                    'count': count,
                    'sort': sort,
                    'direction': direction
                }
                
                if next_index is not None:
                    params['index'] = next_index
                    
                logger.info(f"Fetching digest topics for group {self.group_name}, index={next_index}")
                data = self._make_request(url, params)
                
                if not data.get('succeeded'):
                    break
                    
                next_index = data.get('resp_data', {}).get('index')
                topics_data = data.get('resp_data', {}).get('topics', [])
                
                if not topics_data:
                    logger.info(f"No more digest topics for group {self.group_name}")
                    break
                    
                current_batch = []
                for topic_data in topics_data:
                    try:
                        topic = SimpleTopic.from_dict(topic_data)
                        # If we find the last processed topic ID, stop processing
                        if last_topic_id and topic.topic_id == last_topic_id:
                            logger.info(f"Found already processed digest topic ID: {topic.topic_id} for group {self.group_name}, stopping")
                            found_last_topic = True
                            break

                        topic_detail = self.get_topic_detail(topic.topic_id)
                        if topic_detail:
                            current_batch.append(topic_detail)
                    except Exception as e:
                        logger.error(f"Failed to process topic data: {str(e)}")
                        continue
                
                # Stop if we found the last topic or no new topics in this batch
                if found_last_topic:
                    if len(current_batch) > 0:
                        all_topics.extend(current_batch)
                    break
                    
                # Add this batch to the total list
                all_topics.extend(current_batch)
                
                # Stop if no more pages
                if not next_index:
                    logger.info(f"No more digest topics for group {self.group_name}")
                    break
                    
                time.sleep(1)  # Avoid too frequent requests
                
            except Exception as e:
                logger.error(f"Failed to get digest topics for group {self.group_name}: {str(e)}")
                break
        
        if not all_topics:
            return [], None
            
        # Get the oldest topic as last_topic_id
        oldest_topic = max(all_topics, key=lambda x: x.create_time)
        return all_topics, oldest_topic.topic_id

    def crawl_home_topics(self, last_topic_id=None, last_topic_create_time=None) -> Tuple[List[Topic], Optional[str]]:
        """
        Crawl home page topics
        
        Args:
            last_topic_id: Last crawled topic ID
            
        Returns:
            tuple: (topics, last_topic_id)
        """
        all_topics = []
        end_time = None
        found_last_topic = False
        
        while True:
            try:
                url = f"{self.base_url}/groups/{self.group_id}/topics"
                params = {
                    'scope': 'all',
                    'count': 20
                }
                if end_time:
                    params['end_time'] = end_time
                    
                logger.info(f"Fetching home topics for group {self.group_name}, end_time={end_time}")
                data = self._make_request(url, params)
                
                topics_data = data.get('resp_data', {}).get('topics', [])
                if not topics_data:
                    logger.info(f"No more topics for group {self.group_name}")
                    break
                    
                current_batch = []
                oldest_topic = None
                
                for topic_data in topics_data:
                    try:
                        topic = Topic.from_dict(topic_data)
                        # If we find the last processed topic ID, stop processing
                        if last_topic_id and topic.topic_id == last_topic_id:
                            logger.info(f"Found already processed topic ID: {topic.topic_id} for group {self.group_name}, stopping")
                            found_last_topic = True
                            break
                        
                        current_batch.append(topic)
                        
                        # Record the oldest topic for next query
                        if not oldest_topic or topic.create_time < oldest_topic.create_time:
                            oldest_topic = topic
                            
                    except Exception as e:
                        logger.error(f"Failed to process topic data: {str(e)}")
                        continue
                
                # Stop if we found the last topic or no new topics in this batch
                if found_last_topic:
                    if current_batch:
                        all_topics.extend(current_batch)
                    break
                    
                # Add this batch to the total list
                all_topics.extend(current_batch)
                
                # Use the oldest topic's time for next query
                if oldest_topic:
                    dt_object = oldest_topic.create_time
                    formatted_time = dt_object.strftime("%Y-%m-%dT%H:%M:%S")
                    milliseconds = f".{dt_object.microsecond // 1000:03d}"
                    timezone_offset = dt_object.strftime("%z") or "+0800"
                    end_time = f"{formatted_time}{milliseconds}{timezone_offset}"
                
                time.sleep(1)  # Avoid too frequent requests
                        
            except Exception as e:
                logger.error(f"Error while crawling content for group {self.group_name}: {str(e)}")
                break
        
        if not all_topics:
            return [], None            
        # Get the oldest topic as last_topic_id
        oldest_overall = max(all_topics, key=lambda x: x.create_time)
        return all_topics, oldest_overall.topic_id
