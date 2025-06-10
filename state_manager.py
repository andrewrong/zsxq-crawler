"""
State persistence manager for the 知识星球 crawler.
"""
import json
import os
from enum import Enum
from typing import Any, Dict, Optional

from config import LAST_CRAWLED_FILE


class CrawlType(Enum):
    """抓取类型枚举"""
    HOME = 'home'  # 首页帖子
    DIGEST = 'digest'  # 精华帖子


class StateManager:
    @staticmethod
    def save_state(crawl_type: CrawlType, state_data: Dict[str, Any]):
        """
        保存爬取状态
        
        Args:
            crawl_type: 抓取类型
            state_data: 状态数据字典
        """
        try:
            # 读取现有状态
            current_state = {}
            if os.path.exists(LAST_CRAWLED_FILE):
                with open(LAST_CRAWLED_FILE, 'r', encoding='utf-8') as f:
                    current_state = json.load(f)
            
            # 更新特定类型的状态
            current_state[crawl_type.value] = state_data
            
            # 保存状态
            with open(LAST_CRAWLED_FILE, 'w', encoding='utf-8') as f:
                json.dump(current_state, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"保存状态失败：{e}")
    
    @staticmethod
    def get_state(crawl_type: CrawlType) -> Optional[Dict[str, Any]]:
        """
        获取特定类型的爬取状态
        
        Args:
            crawl_type: 抓取类型
            
        Returns:
            Dict: 状态数据字典，如果不存在返回 None
        """
        try:
            if os.path.exists(LAST_CRAWLED_FILE):
                with open(LAST_CRAWLED_FILE, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    return state.get(crawl_type.value)
        except Exception as e:
            print(f"读取状态失败：{e}")
        return None
    
    @staticmethod
    def clear_state():
        """Remove the state file if it exists."""
        try:
            if os.path.exists(LAST_CRAWLED_FILE):
                os.remove(LAST_CRAWLED_FILE)
        except Exception as e:
            print(f"Failed to clear state: {e}")
