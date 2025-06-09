"""
State persistence manager for the 知识星球 crawler.
"""
import json
import os

from config import LAST_CRAWLED_FILE


class StateManager:
    @staticmethod
    def save_state(last_topic_id: int):
        """
        保存最后一次爬取的主题 ID
        
        Args:
            last_topic_id: 最后爬取的主题 ID
        """
        try:
            state = {
                'last_topic_id': last_topic_id
            }
            with open(LAST_CRAWLED_FILE, 'w') as f:
                json.dump(state, f)
        except Exception as e:
            print(f"保存状态失败：{e}")
    
    @staticmethod
    def get_state():
        """
        获取上次爬取的主题 ID
        
        Returns:
            int: last_topic_id 如果文件不存在则为 None
        """
        try:
            if os.path.exists(LAST_CRAWLED_FILE):
                with open(LAST_CRAWLED_FILE, 'r') as f:
                    state = json.load(f)
                    return state.get('last_topic_id')
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
