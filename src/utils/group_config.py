from dataclasses import dataclass
from typing import Dict, List, Optional
import json


@dataclass
class GroupConfig:
    """Group configuration data class"""
    group_id: str
    is_crawl_home: bool
    thread_ids: dict[str, str]
    
    def get_thread_id(self, name: str) -> str:
        return self.thread_ids.get(name, '')
    
    def get_thread_ids(self) -> dict[str, str]:
        return self.thread_ids
    
    def get_group_id(self) -> str:
        return self.group_id
    
    def get_is_crawl_home(self) -> bool:
        return self.is_crawl_home

class GroupConfigManager:
    def __init__(self, config_str: str):
        self.group_configs = dict[str, GroupConfig]()  
        self.load_group_configs(config_str)
        
    def load_group_configs(self, config_str: str):
        data = json.loads(config_str)
        for group_id, config in data.items():
            self.group_configs[group_id] = GroupConfig(
                group_id=group_id,
                is_crawl_home=config.get('is_crawl_home', False),
                thread_ids=config.get('thread_ids', {})
            )
    
    def get_group_config(self, group_id: str) -> GroupConfig:
        return self.group_configs.get(group_id, None)

    def get_group_configs(self) -> list[str]:
        return list(self.group_configs.keys())
    
    def is_empty(self) -> bool:
        return len(self.group_configs) == 0
    