"""
State persistence manager for the 知识星球 crawler.
"""
import json
import os
from enum import Enum
from typing import Any, Dict, Optional

from config import LAST_CRAWLED_FILE


class CrawlType(Enum):
    """Crawl type enumeration"""
    HOME = 'home'  # Home page posts
    DIGEST = 'digest'  # Digest posts


class StateManager:
    @staticmethod
    def save_state(group_id: str, crawl_type: CrawlType, state_data: Dict[str, Any]):
        """
        Save crawl state for a specific group and crawl type
        
        Args:
            group_id: Group ID
            crawl_type: Crawl type
            state_data: State data dictionary
        """
        try:
            # Read existing state
            current_state = {}
            if os.path.exists(LAST_CRAWLED_FILE):
                with open(LAST_CRAWLED_FILE, 'r', encoding='utf-8') as f:
                    current_state = json.load(f)
            
            # Initialize group state if not exists
            if group_id not in current_state:
                current_state[group_id] = {}
            
            # Update specific type state for the group
            current_state[group_id][crawl_type.value] = state_data
            
            # Save state
            with open(LAST_CRAWLED_FILE, 'w', encoding='utf-8') as f:
                json.dump(current_state, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Failed to save state: {e}")
    
    @staticmethod
    def get_state(group_id: str, crawl_type: CrawlType) -> Optional[Dict[str, Any]]:
        """
        Get crawl state for a specific group and crawl type
        
        Args:
            group_id: Group ID
            crawl_type: Crawl type
            
        Returns:
            Dict: State data dictionary, None if not exists
        """
        try:
            if os.path.exists(LAST_CRAWLED_FILE):
                with open(LAST_CRAWLED_FILE, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    group_state = state.get(group_id, {})
                    return group_state.get(crawl_type.value)
        except Exception as e:
            print(f"Failed to read state: {e}")
        return None
    
    @staticmethod
    def clear_state(group_id: Optional[str] = None):
        """
        Clear state for a specific group or all groups
        
        Args:
            group_id: Group ID to clear state for, None to clear all states
        """
        try:
            if os.path.exists(LAST_CRAWLED_FILE):
                if group_id is None:
                    os.remove(LAST_CRAWLED_FILE)
                else:
                    with open(LAST_CRAWLED_FILE, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                    if group_id in state:
                        del state[group_id]
                        with open(LAST_CRAWLED_FILE, 'w', encoding='utf-8') as f:
                            json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to clear state: {e}")
