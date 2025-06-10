"""
知识星球 content crawler implementation
"""
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests

from config import COOKIE, ZSXQ_GROUP_ID

from .models import Topic, SimpleTopic


class ZsxqCrawler:
    def __init__(self):
        self.headers = {
            'Cookie': "zsxq_access_token=" + COOKIE,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.group_id = ZSXQ_GROUP_ID
        self.base_url = 'https://api.zsxq.com/v2'
        
    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """发送 API 请求并返回 JSON 响应"""
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"API 请求失败：{e}")
            raise

    def get_topic_detail(self, topic_id: str) -> Optional[Topic]:
        """获取单个话题的详细信息"""
        url = f"{self.base_url}/topics/{topic_id}/info"
        try:
            data = self._make_request(url)
            if data.get('succeeded'):
                topic_data = data['resp_data']['topic']
                return Topic.from_dict(topic_data)
        except Exception as e:
            print(f"获取话题详情失败 (ID: {topic_id}): {e}")
        return None

    def get_digest_topics(self, count: int = 30, sort: str = 'by_create_time', direction: str = 'desc', last_topic_id: Optional[str] = None) -> Tuple[List[Topic], Optional[str]]:
        """
        获取精华主题列表
        
        Args:
            count: 每次获取的数量
            sort: 排序方式 ('by_create_time')
            direction: 排序方向 ('desc' 或 'asc')
            last_topic_id: 上次爬取的最后一个主题 ID
            
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
                    
                print(f"正在获取精华主题，index={next_index}")
                data = self._make_request(url, params)
                
                if not data.get('succeeded'):
                    break
                    
                next_index = data.get('resp_data', {}).get('index')
                topics_data = data.get('resp_data', {}).get('topics', [])
                
                if not topics_data:
                    print("没有更多精华主题了")
                    break
                    
                current_batch = []
                for topic_data in topics_data:
                    try:
                        topic = SimpleTopic.from_dict(topic_data)
                        # 如果遇到已经处理过的主题 ID，说明后面的都是重复的，停止处理
                        if last_topic_id and topic.topic_id == last_topic_id:
                            print(f"发现已处理过的精华主题 ID: {topic.topic_id}，停止处理")
                            found_last_topic = True
                            break

                        topic_detail = self.get_topic_detail(topic.topic_id)
                        if topic_detail:
                            current_batch.append(topic_detail)
                    except Exception as e:
                        print(f"处理主题数据失败：{str(e)}")
                        continue
                
                # 如果发现了上次处理的主题，或者这批没有任何新主题，就停止
                if found_last_topic or not current_batch:
                    break
                    
                # 把这批主题加入总列表
                all_topics.extend(current_batch)
                
                # 如果没有下一页的 index 了，就停止
                if not next_index:
                    print("没有下一页精华主题了")
                    break
                    
                time.sleep(1)  # 避免请求太快
                
            except Exception as e:
                print(f"获取精华主题失败：{str(e)}")
                break
        
        if not all_topics:
            return [], None
            
        # 获取所有主题中最旧的一条作为 last_topic_id
        oldest_topic = max(all_topics, key=lambda x: x.create_time)
        return all_topics, oldest_topic.topic_id

    def crawl_home_topics(self, last_topic_id=None, last_topic_create_time=None) -> Tuple[List[Topic], Optional[str]]:
        """
        抓取主页话题列表
        
        Args:
            last_topic_id: 上次爬取的最后一个主题 ID
            
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
                    
                print(f"正在获取主页消息，end_time={end_time}")
                data = self._make_request(url, params)
                
                topics_data = data.get('resp_data', {}).get('topics', [])
                if not topics_data:
                    print("没有更多消息了")
                    break
                    
                current_batch = []
                oldest_topic = None
                
                for topic_data in topics_data:
                    try:
                        topic = Topic.from_dict(topic_data)
                        # 如果遇到已经处理过的主题 ID，说明后面的都是重复的，停止处理
                        if last_topic_id and topic.topic_id == last_topic_id:
                            print(f"发现已处理过的主题 ID: {topic.topic_id}，停止处理")
                            found_last_topic = True
                            break
                        
                        current_batch.append(topic)
                        
                        # 记录最旧的主题，用于下次查询
                        if not oldest_topic or topic.create_time < oldest_topic.create_time:
                            oldest_topic = topic
                            
                    except Exception as e:
                        print(f"处理主题数据失败：{str(e)}")
                        continue
                
                # 如果发现了上次处理的主题，或者这批没有任何新主题，就停止
                if found_last_topic or not current_batch:
                    break
                    
                # 把这批主题加入总列表
                all_topics.extend(current_batch)
                
                # 使用最旧主题的时间作为下次查询的 end_time
                if oldest_topic:
                    dt_object = oldest_topic.create_time
                    formatted_time = dt_object.strftime("%Y-%m-%dT%H:%M:%S")
                    milliseconds = f".{dt_object.microsecond // 1000:03d}"
                    timezone_offset = dt_object.strftime("%z") or "+0800"
                    end_time = f"{formatted_time}{milliseconds}{timezone_offset}"
                
                time.sleep(1)  # 避免请求太快
                        
            except Exception as e:
                print(f"抓取内容时发生错误：{str(e)}")
                break
        
        if not all_topics:
            return [], None
            
        # 获取所有主题中最旧的一条作为 last_topic_id
        oldest_overall = max(all_topics, key=lambda x: x.create_time)
        return all_topics, oldest_overall.topic_id