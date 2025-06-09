"""
知识星球 content crawler implementation
"""
import json
import time
from datetime import datetime
from urllib.parse import urlparse

import requests

from config import COOKIE, ZSXQ_GROUP_ID

from .models import Topic


class ZsxqCrawler:
    def __init__(self):
        self.headers = {
            'Cookie': "zsxq_access_token=" + COOKIE,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.group_id = ZSXQ_GROUP_ID
        self.base_url = 'https://api.zsxq.com/v2'

    def crawl(self, last_topic_id=None):
        """
        从知识星球抓取内容。会一直获取直到遇到已处理的消息或没有更多消息。
        
        Args:
            last_topic_id: 上次爬取的最后一个主题 ID，用于去重
            
        Returns:
            tuple: (topics, last_topic_id)
                - topics: 主题列表
                - last_topic_id: 本次爬取的最后一个主题 ID
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
                    
                print(f"正在获取消息，end_time={end_time}")
                response = requests.get(url, headers=self.headers, params=params)
                
                if response.status_code != 200:
                    print(f"API 请求失败，状态码：{response.status_code}")
                    break
                    
                data = response.json()
                topics_data = data.get('resp_data', {}).get('topics', [])
                
                if not topics_data:
                    print("没有更多消息了")
                    break
                    
                current_batch = []
                oldest_topic = None
                
                for topic_data in topics_data:
                    try:
                        topic = Topic.from_dict(topic_data)
                        
                        if "如何计算奖励" in topic.title: 
                            conten =json.dumps(topic_data, ensure_ascii=False)
                            print(f"跳过奖励计算主题：{conten}")
                        
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
                    # 格式化时间为 YYYY-MM-DDTHH:MM:SS.mmm<offset>
                    # <offset> (例如 +0800) 从 oldest_topic.create_time 动态获取
                    dt_object = oldest_topic.create_time
                    
                    formatted_time = dt_object.strftime("%Y-%m-%dT%H:%M:%S")
                    milliseconds = f".{dt_object.microsecond // 1000:03d}"
                    # 获取时区偏移，例如 +0800。如果 datetime 对象是 naive 的，则为空字符串。
                    timezone_offset = dt_object.strftime("%z") 
                    
                    if not timezone_offset:
                        timezone_offset = "+0800"
                    
                    end_time = f"{formatted_time}{milliseconds}{timezone_offset}"
                
                # 避免请求太快
                time.sleep(1)
                        
            except Exception as e:
                print(f"抓取内容时发生错误：{str(e)}")
                break
        
        if not all_topics:
            return [], None
            
        # 获取所有主题中最旧的一条作为 last_topic_id
        oldest_overall = min(all_topics, key=lambda x: x.create_time)
        return all_topics, oldest_overall.topic_id